/**
 * 3D Port Visualization using Three.js
 * 
 * Visualizes:
 * - Berths as colored boxes (status: free/blue, reserved/yellow, occupied/red)
 * - Vessels as capsules docked at berths
 * - Sensors as points in the 3D space
 * - Alerts as warning icons
 * 
 * Real-time updates from WebSocket
 */

class Map3D {
  constructor(containerId = 'map-3d') {
    this.container = document.getElementById(containerId);
    if (!containerId || !this.container) {
      console.error('[Map3D] Container not found:', containerId);
      return;
    }

    // Three.js objects
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;

    // Visualization objects
    this.berthMeshes = {};    // { berth_id: Mesh }
    this.vesselMeshes = {};   // { vessel_id: Mesh }
    this.sensorMeshes = {};   // { sensor_id: Mesh }
    this.alertMeshes = {};    // { alert_id: Mesh }

    // Color scheme
    this.colors = {
      free: 0x4CAF50,        // Green
      reserved: 0xFFC107,    // Amber
      occupied: 0xF44336,    // Red
      unavailable: 0x9E9E9E, // Gray
      vessel: 0x2196F3,      // Blue
      sensor: 0xFF9800,      // Orange
      alert: 0xE91E63,       // Pink
      water: 0x00BCD4,       // Cyan
      grid: 0xCCCCCC,        // Light gray
    };

    this.debug = window.ENV?.DEBUG || false;
    
    this._init();
  }

  _init() {
    try {
      // Scene setup
      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color(0xF5F5F5);
      this.scene.fog = new THREE.Fog(0xF5F5F5, 500, 1500);

      // Camera setup
      const width = this.container.clientWidth;
      const height = this.container.clientHeight;
      this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 2000);
      this.camera.position.set(0, 100, 150);
      this.camera.lookAt(0, 0, 0);

      // Renderer setup
      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(window.devicePixelRatio);
      this.renderer.shadowMap.enabled = true;
      this.container.appendChild(this.renderer.domElement);

      // Lighting
      this._setupLighting();

      // Environment
      this._setupEnvironment();

      // Start rendering loop
      this._startRenderLoop();

      // Handle window resize
      window.addEventListener('resize', () => this._onWindowResize());

      if (this.debug) {
        console.log('[Map3D] Initialized successfully');
      }
    } catch (error) {
      console.error('[Map3D] Initialization error:', error);
    }
  }

  _setupLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.6);
    this.scene.add(ambientLight);

    // Directional light
    const directionalLight = new THREE.DirectionalLight(0xFFFFFF, 0.8);
    directionalLight.position.set(100, 200, 100);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.left = -300;
    directionalLight.shadow.camera.right = 300;
    directionalLight.shadow.camera.top = 300;
    directionalLight.shadow.camera.bottom = -300;
    this.scene.add(directionalLight);
  }

  _setupEnvironment() {
    // Ground plane (water/dock area)
    const groundGeometry = new THREE.PlaneGeometry(400, 400);
    const groundMaterial = new THREE.MeshPhongMaterial({ color: this.colors.water, shininess: 100 });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    this.scene.add(ground);

    // Grid helper
    const gridHelper = new THREE.GridHelper(400, 40, this.colors.grid, this.colors.grid);
    gridHelper.position.y = 0.1;
    this.scene.add(gridHelper);

    // Axes helper (for debugging)
    if (this.debug) {
      const axesHelper = new THREE.AxesHelper(100);
      this.scene.add(axesHelper);
    }
  }

  /**
   * Add or update berth visualization
   */
  updateBerth(berthId, berthData) {
    try {
      if (this.berthMeshes[berthId]) {
        // Update existing berth
        this._updateBerthColor(berthId, berthData.status);
      } else {
        // Create new berth
        this._createBerthMesh(berthId, berthData);
      }
    } catch (error) {
      console.error('[Map3D] Error updating berth:', error);
    }
  }

  _createBerthMesh(berthId, berthData) {
    const { status = 'free', position_index = 0 } = berthData;

    // Position berths in a grid
    const row = Math.floor(position_index / 5);
    const col = position_index % 5;
    const x = col * 70 - 140;
    const z = row * 70 - 140;

    // Berth geometry (box: 30m long, 20m wide, 15m tall)
    const geometry = new THREE.BoxGeometry(30, 15, 20);
    const color = this.colors[status] || this.colors.free;
    const material = new THREE.MeshPhongMaterial({
      color: color,
      shininess: 100,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(x, 7.5, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData = { type: 'berth', id: berthId, status };

    // Add label above berth
    this._addBerthLabel(mesh, berthId);

    this.scene.add(mesh);
    this.berthMeshes[berthId] = mesh;

    if (this.debug) {
      console.log('[Map3D] Berth created:', berthId, status, { x, z });
    }
  }

  _updateBerthColor(berthId, status) {
    const mesh = this.berthMeshes[berthId];
    if (mesh) {
      const newColor = this.colors[status] || this.colors.free;
      mesh.material.color.setHex(newColor);
      mesh.userData.status = status;

      if (this.debug) {
        console.log('[Map3D] Berth color updated:', berthId, status);
      }
    }
  }

  _addBerthLabel(berthMesh, berthId) {
    // Simple label (using canvas texture or DOM elements)
    // For now, just store the ID in userData
    const label = berthId.split(':').pop(); // Extract short name
    berthMesh.userData.label = label;
  }

  /**
   * Add or update vessel visualization
   */
  updateVessel(vesselId, vesselData) {
    try {
      if (this.vesselMeshes[vesselId]) {
        // Update existing vessel
        this._updateVesselPosition(vesselId, vesselData);
      } else {
        // Create new vessel
        this._createVesselMesh(vesselId, vesselData);
      }
    } catch (error) {
      console.error('[Map3D] Error updating vessel:', error);
    }
  }

  _createVesselMesh(vesselId, vesselData) {
    const {
      length_m = 200,
      beam_m = 30,
      draft_m = 10,
      berth_id = null,
    } = vesselData;

    // Normalize dimensions
    const length = Math.max(20, length_m / 5);  // Scale down for visualization
    const width = Math.max(10, beam_m / 3);
    const height = Math.max(8, draft_m / 2);

    // Vessel geometry (capsule shape: cylinder + hemispheres)
    const geometry = new THREE.CapsuleGeometry(width / 2, length, 4, 8);
    const material = new THREE.MeshPhongMaterial({
      color: this.colors.vessel,
      shininess: 120,
      wireframe: false,
    });
    const mesh = new THREE.Mesh(geometry, material);

    // Position: if docked, place at berth; otherwise in the harbor
    if (berth_id && this.berthMeshes[berth_id]) {
      const berthMesh = this.berthMeshes[berth_id];
      mesh.position.copy(berthMesh.position);
      mesh.position.y = height / 2 + 10;
      mesh.rotation.z = Math.PI / 2;
    } else {
      // Free floating in harbor
      mesh.position.set(
        (Math.random() - 0.5) * 200,
        height / 2,
        (Math.random() - 0.5) * 200
      );
    }

    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData = {
      type: 'vessel',
      id: vesselId,
      length_m,
      beam_m,
      draft_m,
    };

    this.scene.add(mesh);
    this.vesselMeshes[vesselId] = mesh;

    if (this.debug) {
      console.log('[Map3D] Vessel created:', vesselId, { length_m, beam_m });
    }
  }

  _updateVesselPosition(vesselId, vesselData) {
    const mesh = this.vesselMeshes[vesselId];
    if (mesh && vesselData.berth_id && this.berthMeshes[vesselData.berth_id]) {
      // Move vessel to berth
      const berthMesh = this.berthMeshes[vesselData.berth_id];
      mesh.position.copy(berthMesh.position);
      mesh.position.y += 10;

      if (this.debug) {
        console.log('[Map3D] Vessel repositioned:', vesselId);
      }
    }
  }

  /**
   * Add or update sensor visualization
   */
  updateSensor(sensorId, sensorData) {
    try {
      if (this.sensorMeshes[sensorId]) {
        // Update existing sensor
        const mesh = this.sensorMeshes[sensorId];
        mesh.userData = { ...mesh.userData, ...sensorData };
      } else {
        // Create new sensor
        this._createSensorMesh(sensorId, sensorData);
      }
    } catch (error) {
      console.error('[Map3D] Error updating sensor:', error);
    }
  }

  _createSensorMesh(sensorId, sensorData) {
    const { sensor_type = 'generic' } = sensorData;

    // Sensor geometry (small sphere)
    const geometry = new THREE.SphereGeometry(5, 16, 16);
    const material = new THREE.MeshPhongMaterial({
      color: this.colors.sensor,
      emissive: 0xFF6600,
      shininess: 60,
    });
    const mesh = new THREE.Mesh(geometry, material);

    // Random position in harbor
    mesh.position.set(
      (Math.random() - 0.5) * 300,
      30,
      (Math.random() - 0.5) * 300
    );

    mesh.castShadow = true;
    mesh.userData = {
      type: 'sensor',
      id: sensorId,
      sensor_type,
    };

    this.scene.add(mesh);
    this.sensorMeshes[sensorId] = mesh;

    if (this.debug) {
      console.log('[Map3D] Sensor created:', sensorId, sensor_type);
    }
  }

  /**
   * Add or remove alert visualization
   */
  updateAlert(alertId, alertData, remove = false) {
    try {
      if (remove) {
        if (this.alertMeshes[alertId]) {
          this.scene.remove(this.alertMeshes[alertId]);
          delete this.alertMeshes[alertId];
        }
      } else {
        this._createAlertMesh(alertId, alertData);
      }
    } catch (error) {
      console.error('[Map3D] Error updating alert:', error);
    }
  }

  _createAlertMesh(alertId, alertData) {
    const { entity_id = null, severity = 'warning' } = alertData;

    // Alert geometry (cone)
    const geometry = new THREE.ConeGeometry(10, 20, 8);
    const material = new THREE.MeshPhongMaterial({
      color: this.colors.alert,
      emissive: severity === 'critical' ? 0xFF0000 : 0xFF69B4,
      shininess: 100,
    });
    const mesh = new THREE.Mesh(geometry, material);

    // Position above entity if possible
    if (entity_id && this.berthMeshes[entity_id]) {
      const berthMesh = this.berthMeshes[entity_id];
      mesh.position.copy(berthMesh.position);
      mesh.position.y += 50;
    } else {
      // Random position
      mesh.position.set(
        (Math.random() - 0.5) * 200,
        100,
        (Math.random() - 0.5) * 200
      );
    }

    mesh.castShadow = true;
    mesh.userData = {
      type: 'alert',
      id: alertId,
      severity,
    };

    this.scene.add(mesh);
    this.alertMeshes[alertId] = mesh;

    // Animate alert cone (pulsing)
    this._animateAlert(mesh);

    if (this.debug) {
      console.log('[Map3D] Alert created:', alertId, severity);
    }
  }

  _animateAlert(mesh) {
    // Simple pulsing animation using scale
    const originalScale = mesh.scale.y;
    const animation = setInterval(() => {
      if (!this.alertMeshes[mesh.userData.id]) {
        clearInterval(animation);
        return;
      }
      mesh.scale.y = originalScale * (0.8 + Math.sin(Date.now() / 200) * 0.2);
    }, 50);
  }

  /**
   * Load initial snapshot of entities
   */
  loadSnapshot(snapshotData) {
    try {
      if (snapshotData.berths) {
        Object.entries(snapshotData.berths).forEach(([berthId, berthData]) => {
          this.updateBerth(berthId, berthData);
        });
      }

      if (snapshotData.vessels) {
        Object.entries(snapshotData.vessels).forEach(([vesselId, vesselData]) => {
          this.updateVessel(vesselId, vesselData);
        });
      }

      if (snapshotData.sensors) {
        Object.entries(snapshotData.sensors).forEach(([sensorId, sensorData]) => {
          this.updateSensor(sensorId, sensorData);
        });
      }

      if (this.debug) {
        console.log('[Map3D] Snapshot loaded');
      }
    } catch (error) {
      console.error('[Map3D] Error loading snapshot:', error);
    }
  }

  /**
   * Handle mouse click for object selection
   */
  _onMouseClick(event) {
    if (!this.renderer) return;

    const rect = this.renderer.domElement.getBoundingClientRect();
    const mouse = new THREE.Vector2();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mouse, this.camera);

    const objects = [
      ...Object.values(this.berthMeshes),
      ...Object.values(this.vesselMeshes),
      ...Object.values(this.sensorMeshes),
    ];

    const intersects = raycaster.intersectObjects(objects);
    if (intersects.length > 0) {
      const selected = intersects[0].object;
      this._selectObject(selected);
    }
  }

  _selectObject(mesh) {
    // Highlight selected object
    if (this.selectedMesh) {
      this.selectedMesh.material.emissive.setHex(0x000000);
    }

    mesh.material.emissive.setHex(0x444444);
    this.selectedMesh = mesh;

    if (this.debug) {
      console.log('[Map3D] Selected:', mesh.userData);
    }

    // Emit event to show details panel
    window.dispatchEvent(new CustomEvent('3d:objectSelected', { detail: mesh.userData }));
  }

  /**
   * Main render loop
   */
  _startRenderLoop() {
    const animate = () => {
      requestAnimationFrame(animate);

      // Subtle rotation of camera around scene
      const time = Date.now() * 0.0001;
      if (true) {  // Auto-rotate disabled for now
        // this.camera.position.x = Math.sin(time) * 200;
        // this.camera.position.z = Math.cos(time) * 200;
      }

      this.renderer.render(this.scene, this.camera);
    };

    animate();
    this.renderer.domElement.addEventListener('click', (e) => this._onMouseClick(e));
  }

  /**
   * Handle window resize
   */
  _onWindowResize() {
    if (!this.container || !this.renderer) return;

    const width = this.container.clientWidth;
    const height = this.container.clientHeight;

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  /**
   * Clean up resources
   */
  destroy() {
    if (this.renderer) {
      this.renderer.dispose();
      this.container.removeChild(this.renderer.domElement);
    }
  }
}

export default Map3D;
