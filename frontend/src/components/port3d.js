/**
 * Port3DController - Three.js schematic 3D view of a port's berths
 *
 * Renders 12 berths as colored boxes along a pier.
 * Colors encode status: green=free, red=occupied, yellow=reserved, gray=unavailable.
 * Supports mouse-drag orbit, scroll zoom, and hover tooltips.
 * Connects to WS bus via updateBerth() for live state changes.
 */

const STATUS_COLORS = {
  free:            0x2ecc71,
  occupied:        0xe74c3c,
  reserved:        0xf39c12,
  unavailable:     0x7f8c8d,
  out_of_service:  0x95a5a6,
};

const STATUS_LABELS = {
  free: 'Libre',
  occupied: 'Ocupado',
  reserved: 'Reservado',
  unavailable: 'No disponible',
  out_of_service: 'Fuera de servicio',
};

export class Port3DController {
  constructor(containerId) {
    this.containerId = containerId;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.berthMeshes = {};  // berthId -> THREE.Mesh
    this.animId = null;
    this._tooltip = null;
    this._raycaster = null;
    this._mouse = null;
    this._resizeHandler = null;
    // Spherical orbit state
    this._theta = 0.6;     // azimuth
    this._phi = 0.55;      // elevation
    this._radius = 65;
    this._dragging = false;
    this._lastX = 0;
    this._lastY = 0;
  }

  init(berths) {
    const THREE = window.THREE;
    if (!THREE) {
      console.error('[Port3D] Three.js (r128) not available on window.THREE');
      return false;
    }

    const container = document.getElementById(this.containerId);
    if (!container) return false;

    const w = container.clientWidth || 800;
    const h = container.clientHeight || 500;

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x1a3a5c);
    this.scene.fog = new THREE.FogExp2(0x1a3a5c, 0.006);

    // Camera
    this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 600);
    this._updateCamera();

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(w, h);
    this.renderer.shadowMap.enabled = true;
    container.appendChild(this.renderer.domElement);

    // Lights
    const ambient = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambient);
    const sun = new THREE.DirectionalLight(0xfff5e6, 1.4);
    sun.position.set(50, 100, 50);
    sun.castShadow = true;
    this.scene.add(sun);
    const fill = new THREE.DirectionalLight(0xadd8e6, 0.4);
    fill.position.set(-30, 20, -30);
    this.scene.add(fill);

    // Water plane
    const waterGeo = new THREE.PlaneGeometry(300, 300);
    const waterMat = new THREE.MeshPhongMaterial({
      color: 0x006994,
      shininess: 80,
      specular: 0x88ccee,
    });
    const water = new THREE.Mesh(waterGeo, waterMat);
    water.rotation.x = -Math.PI / 2;
    water.position.y = -0.6;
    this.scene.add(water);

    // Pier platform
    const pierGeo = new THREE.BoxGeometry(72, 1.5, 9);
    const pierMat = new THREE.MeshPhongMaterial({ color: 0x7a7a7a });
    const pier = new THREE.Mesh(pierGeo, pierMat);
    pier.position.set(0, 0, 0);
    pier.receiveShadow = true;
    this.scene.add(pier);

    // Pier front yellow safety edge
    const edgeGeo = new THREE.BoxGeometry(72, 0.3, 0.4);
    const edgeMat = new THREE.MeshPhongMaterial({ color: 0xf1c40f });
    const edge = new THREE.Mesh(edgeGeo, edgeMat);
    edge.position.set(0, 0.9, 4.6);
    this.scene.add(edge);

    // Pier bollards (small cylinders)
    const bollardGeo = new THREE.CylinderGeometry(0.2, 0.2, 1, 8);
    const bollardMat = new THREE.MeshPhongMaterial({ color: 0x333333 });
    for (let i = -5; i <= 5; i++) {
      const b = new THREE.Mesh(bollardGeo, bollardMat);
      b.position.set(i * 6, 1.25, 4.2);
      this.scene.add(b);
    }

    // Berths
    this._addBerths(THREE, berths);

    // Mouse controls
    this._setupControls(container);

    // Hover tooltip
    this._setupTooltip(container);

    // Resize
    this._resizeHandler = () => this._onResize(container);
    window.addEventListener('resize', this._resizeHandler);

    // Start render loop
    this._animate();

    return true;
  }

  _addBerths(THREE, berths) {
    const count = berths.length || 1;
    const totalWidth = 66;
    const spacing = totalWidth / count;
    const startX = -(totalWidth / 2) + spacing / 2;

    berths.forEach((berth, i) => {
      const color = STATUS_COLORS[berth.status] || 0xbdc3c7;
      const berthW = spacing * 0.78;
      const geo = new THREE.BoxGeometry(berthW, 2.5, 6.5);
      const mat = new THREE.MeshPhongMaterial({ color, shininess: 60 });
      const mesh = new THREE.Mesh(geo, mat);
      const x = startX + i * spacing;
      mesh.position.set(x, 1.5, 6);
      mesh.castShadow = true;
      mesh.userData = {
        berthId: berth.id,
        berthName: berth.name || `Berth ${i + 1}`,
        status: berth.status || 'unknown',
      };
      this.scene.add(mesh);
      this.berthMeshes[berth.id] = mesh;

      // Number label sprite
      this._addLabel(THREE, { x, y: 3.5, z: 6 }, String(i + 1));
    });
  }

  _addLabel(THREE, pos, text) {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.beginPath();
    ctx.arc(32, 32, 30, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 28px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 32, 32);

    const tex = new THREE.CanvasTexture(canvas);
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(2.2, 2.2, 1);
    sprite.position.set(pos.x, pos.y, pos.z);
    this.scene.add(sprite);
  }

  updateBerth(berthId, status) {
    const mesh = this.berthMeshes[berthId];
    if (!mesh) return;
    const color = STATUS_COLORS[status] || 0xbdc3c7;
    mesh.material.color.setHex(color);
    mesh.userData.status = status;
    // Brief pulse: scale up then back
    mesh.scale.set(1.12, 1.12, 1.12);
    setTimeout(() => { if (mesh) mesh.scale.set(1, 1, 1); }, 350);
  }

  _updateCamera() {
    const sinPhi = Math.sin(this._phi);
    const x = this._radius * sinPhi * Math.sin(this._theta);
    const y = this._radius * Math.cos(this._phi);
    const z = this._radius * sinPhi * Math.cos(this._theta);
    this.camera.position.set(x, y, z);
    this.camera.lookAt(0, 1, 3);
  }

  _setupControls(container) {
    const onDown = (e) => {
      this._dragging = true;
      this._lastX = e.clientX ?? e.touches?.[0]?.clientX;
      this._lastY = e.clientY ?? e.touches?.[0]?.clientY;
    };
    const onMove = (e) => {
      if (!this._dragging) return;
      const cx = e.clientX ?? e.touches?.[0]?.clientX;
      const cy = e.clientY ?? e.touches?.[0]?.clientY;
      this._theta -= (cx - this._lastX) * 0.008;
      this._phi = Math.max(0.15, Math.min(Math.PI / 2.1, this._phi + (cy - this._lastY) * 0.008));
      this._lastX = cx;
      this._lastY = cy;
      this._updateCamera();
    };
    const onUp = () => { this._dragging = false; };

    container.addEventListener('mousedown', onDown);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    container.addEventListener('touchstart', onDown, { passive: true });
    window.addEventListener('touchmove', onMove, { passive: true });
    window.addEventListener('touchend', onUp);

    container.addEventListener('wheel', (e) => {
      e.preventDefault();
      this._radius = Math.max(25, Math.min(130, this._radius + e.deltaY * 0.08));
      this._updateCamera();
    }, { passive: false });
  }

  _setupTooltip(container) {
    const tip = document.createElement('div');
    tip.style.cssText = [
      'position:absolute',
      'background:rgba(10,20,40,0.88)',
      'color:#fff',
      'padding:8px 12px',
      'border-radius:6px',
      'font-size:13px',
      'line-height:1.5',
      'pointer-events:none',
      'display:none',
      'z-index:20',
      'border:1px solid rgba(255,255,255,0.15)',
    ].join(';');
    container.style.position = 'relative';
    container.appendChild(tip);
    this._tooltip = tip;

    this._raycaster = new window.THREE.Raycaster();
    this._mouse = new window.THREE.Vector2();

    this.renderer.domElement.addEventListener('mousemove', (e) => {
      const rect = this.renderer.domElement.getBoundingClientRect();
      this._mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this._mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      this._raycaster.setFromCamera(this._mouse, this.camera);
      const hits = this._raycaster.intersectObjects(Object.values(this.berthMeshes));

      if (hits.length > 0) {
        const { berthName, status } = hits[0].object.userData;
        const statusLabel = STATUS_LABELS[status] || status;
        tip.innerHTML = `<strong>${berthName}</strong><br><span style="color:${this._statusColorHex(status)}">● ${statusLabel}</span>`;
        tip.style.display = 'block';
        tip.style.left = (e.clientX - rect.left + 14) + 'px';
        tip.style.top = (e.clientY - rect.top - 10) + 'px';
      } else {
        tip.style.display = 'none';
      }
    });

    this.renderer.domElement.addEventListener('mouseleave', () => {
      tip.style.display = 'none';
    });
  }

  _statusColorHex(status) {
    const map = {
      free: '#2ecc71', occupied: '#e74c3c',
      reserved: '#f39c12', unavailable: '#7f8c8d', out_of_service: '#95a5a6',
    };
    return map[status] || '#bdc3c7';
  }

  _onResize(container) {
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w === 0 || h === 0) return;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  _animate() {
    this.animId = requestAnimationFrame(() => this._animate());
    this.renderer.render(this.scene, this.camera);
  }

  destroy() {
    cancelAnimationFrame(this.animId);
    if (this._resizeHandler) window.removeEventListener('resize', this._resizeHandler);
    if (this.renderer) {
      this.renderer.dispose();
      const canvas = this.renderer.domElement;
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
    }
    if (this._tooltip && this._tooltip.parentNode) {
      this._tooltip.parentNode.removeChild(this._tooltip);
    }
    this.berthMeshes = {};
    this.scene = null;
    this.renderer = null;
  }
}
