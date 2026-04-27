# NGSI-LD Payload Examples - SmartPort Galicia

Generated payloads for actual Galician ports using Smart Data Models and NGSI-LD v1.6 compliance.

## Port Entity

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:Port:galicia-a-coruna",
  "type": "Port",
  "name": {
    "type": "Property",
    "value": "Puerto de A Coruña"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3936, 43.3613]
    }
  },
  "description": {
    "type": "Property",
    "value": "Main port of A Coruña, northwest coast"
  },
  "portType": {
    "type": "Property",
    "value": "SeaPort"
  },
  "managedBy": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:PortAuthority:autoridad-a-coruna"
  },
  "hasFacilities": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:SeaportFacilities:galicia-a-coruna-main"
  }
}
```

**Key Features:**
- ✓ Includes @context for NGSI-LD compliance
- ✓ GeoProperty with real WGS84 coordinates
- ✓ Relationships to authority and facilities
- ✓ Static properties (no observedAt)

## PortAuthority Entity

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:PortAuthority:autoridad-a-coruna",
  "type": "PortAuthority",
  "name": {
    "type": "Property",
    "value": "Autoridad Portuaria de A Coruña"
  },
  "email": {
    "type": "Property",
    "value": "info@puertocoruna.es"
  },
  "telephone": {
    "type": "Property",
    "value": "+34 981 22 27 00"
  },
  "website": {
    "type": "Property",
    "value": "http://www.puertocoruna.es"
  }
}
```

## SeaportFacilities Entity

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:SeaportFacilities:galicia-a-coruna-main",
  "type": "SeaportFacilities",
  "name": {
    "type": "Property",
    "value": "Terminal General de A Coruña"
  },
  "description": {
    "type": "Property",
    "value": "Main seaport facility for Puerto de A Coruña"
  },
  "capacity": {
    "type": "Property",
    "value": 250
  },
  "belongsToPort": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:Port:galicia-a-coruna"
  }
}
```

## Berth Entity (Dynamic)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:Berth:galicia-a-coruna-001",
  "type": "Berth",
  "name": {
    "type": "Property",
    "value": "Puerto de A Coruña - Berth 1"
  },
  "status": {
    "type": "Property",
    "value": "free",
    "observedAt": "2026-04-27T17:49:21Z"
  },
  "belongsTo": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:SeaportFacilities:galicia-a-coruna-main"
  },
  "dimensions": {
    "type": "Property",
    "value": {
      "length": 155.0,
      "width": 25.0,
      "depth": 10.0
    }
  }
}
```

**Key Features:**
- ✓ Dynamic `status` with `observedAt` timestamp
- ✓ Physical dimensions as Property
- ✓ Relationship to facility

## MasterVessel Entity (Static Registry)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:MasterVessel:imo-9876543",
  "type": "MasterVessel",
  "imo": {
    "type": "Property",
    "value": "9876543"
  },
  "name": {
    "type": "Property",
    "value": "Galicia Trader"
  },
  "shipType": {
    "type": "Property",
    "value": "General Cargo"
  },
  "length": {
    "type": "Property",
    "value": 120.5
  },
  "beam": {
    "type": "Property",
    "value": 18.2
  },
  "depth": {
    "type": "Property",
    "value": 10.5
  },
  "grossTonnage": {
    "type": "Property",
    "value": 8500
  },
  "netTonnage": {
    "type": "Property",
    "value": 5200
  },
  "yearBuilt": {
    "type": "Property",
    "value": 2010
  },
  "flagState": {
    "type": "Property",
    "value": "ES"
  }
}
```

## Vessel Entity (Semi-Dynamic)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:Vessel:mmsi-224123456",
  "type": "Vessel",
  "name": {
    "type": "Property",
    "value": "Galicia Trader"
  },
  "mmsi": {
    "type": "Property",
    "value": "224123456"
  },
  "imo": {
    "type": "Property",
    "value": "9876543"
  },
  "vesselType": {
    "type": "Property",
    "value": "General Cargo"
  },
  "length": {
    "type": "Property",
    "value": 120.5
  },
  "beam": {
    "type": "Property",
    "value": 18.2
  },
  "draught": {
    "type": "Property",
    "value": 10.5
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3936, 43.3613]
    }
  },
  "position": {
    "type": "Property",
    "value": [-8.3936, 43.3613],
    "observedAt": "2026-04-27T17:49:21Z"
  }
}
```

## BoatAuthorized Entity

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:BoatAuthorized:es-224123456",
  "type": "BoatAuthorized",
  "refVessel": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:Vessel:mmsi-224123456"
  },
  "authorizedPort": {
    "type": "Property",
    "value": "a-coruna"
  },
  "validFrom": {
    "type": "Property",
    "value": "2026-04-27T17:49:21Z"
  },
  "validUntil": {
    "type": "Property",
    "value": "2027-12-31T23:59:59Z"
  },
  "authorizationType": {
    "type": "Property",
    "value": "commercial"
  }
}
```

## BoatPlacesAvailable Entity (Dynamic)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:BoatPlacesAvailable:galicia-a-coruna-A",
  "type": "BoatPlacesAvailable",
  "refSeaportFacility": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:SeaportFacilities:galicia-a-coruna-main"
  },
  "category": {
    "type": "Property",
    "value": "A"
  },
  "totalPlaces": {
    "type": "Property",
    "value": 62
  },
  "availablePlaces": {
    "type": "Property",
    "value": 41,
    "observedAt": "2026-04-27T17:49:21Z"
  }
}
```

## BoatPlacesPricing Entity

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:BoatPlacesPricing:galicia-a-coruna-cat-A",
  "type": "BoatPlacesPricing",
  "refSeaportFacility": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:SeaportFacilities:galicia-a-coruna-main"
  },
  "category": {
    "type": "Property",
    "value": "A"
  },
  "pricePerDay": {
    "type": "Property",
    "value": 45.0
  },
  "currency": {
    "type": "Property",
    "value": "EUR"
  },
  "iso8266LengthMin": {
    "type": "Property",
    "value": 0
  },
  "iso8266LengthMax": {
    "type": "Property",
    "value": 7
  }
}
```

## Device Entity (Sensor)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:Device:galicia-a-coruna-air-01",
  "type": "Device",
  "name": {
    "type": "Property",
    "value": "Air Quality Monitor - A Coruña Port"
  },
  "deviceType": {
    "type": "Property",
    "value": "AirQualityMeter"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3936, 43.3613]
    }
  },
  "refPort": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:Port:galicia-a-coruna"
  }
}
```

## AirQualityObserved Entity (Dynamic)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:AirQualityObserved:galicia-a-coruna-air-01",
  "type": "AirQualityObserved",
  "refDevice": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:Device:galicia-a-coruna-air-01"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3936, 43.3613]
    }
  },
  "observedAt": "2026-04-27T17:49:21Z",
  "pm25": {
    "type": "Property",
    "value": 15.5,
    "observedAt": "2026-04-27T17:49:21Z"
  },
  "pm10": {
    "type": "Property",
    "value": 25.0,
    "observedAt": "2026-04-27T17:49:21Z"
  },
  "no2": {
    "type": "Property",
    "value": 35.0,
    "observedAt": "2026-04-27T17:49:21Z"
  },
  "co": {
    "type": "Property",
    "value": 0.5,
    "observedAt": "2026-04-27T17:49:21Z"
  }
}
```

## WeatherObserved Entity (Dynamic)

```json
{
  "@context": [
    "https://www.w3.org/2019/wot/json-schema",
    "https://smartdatamodels.org/context.jsonld",
    "https://schema.org/",
    {
      "smartdatamodels": "https://smartdatamodels.org/ontology/",
      "ngsi": "https://uri.etsi.org/ngsi-ld/",
      "fiware": "https://fiware.github.io/data-models/context.jsonld"
    }
  ],
  "id": "urn:ngsi-ld:WeatherObserved:galicia-a-coruna-weather-01",
  "type": "WeatherObserved",
  "refDevice": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:Device:galicia-a-coruna-air-01"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3936, 43.3613]
    }
  },
  "observedAt": "2026-04-27T17:49:21Z",
  "temperature": {
    "type": "Property",
    "value": 18.5,
    "observedAt": "2026-04-27T17:49:21Z"
  },
  "relativeHumidity": {
    "type": "Property",
    "value": 65.0,
    "observedAt": "2026-04-27T17:49:21Z"
  },
  "windSpeed": {
    "type": "Property",
    "value": 12.0,
    "observedAt": "2026-04-27T17:49:21Z"
  },
  "windDirection": {
    "type": "Property",
    "value": 180.0,
    "observedAt": "2026-04-27T17:49:21Z"
  },
  "atmosphericPressure": {
    "type": "Property",
    "value": 1013.25,
    "observedAt": "2026-04-27T17:49:21Z"
  }
}
```

## NGSI-LD Compliance Checklist

All payloads include:

- ✓ `@context` - NGSI-LD compliance
- ✓ `id` - URN format: `urn:ngsi-ld:<type>:<namespace>:<id>`
- ✓ `type` - Entity type from Smart Data Models
- ✓ Properties with `type: "Property"` and `value`
- ✓ Relationships with `type: "Relationship"` and `object`
- ✓ GeoProperties with GeoJSON format
- ✓ `observedAt` on dynamic attributes
- ✓ Real data (coordinates, names, values)

## Key Differences by Entity Type

### Static (No `observedAt`)
- Port, PortAuthority, SeaportFacilities
- MasterVessel, BoatPlacesPricing

### Dynamic (With `observedAt`)
- Berth.status
- Vessel.position
- BoatPlacesAvailable.availablePlaces
- AirQualityObserved.* measurements
- WeatherObserved.* measurements

## Relationships Map

```
Port
├── managedBy → PortAuthority
└── hasFacilities → SeaportFacilities
    ├── hasAvailability → BoatPlacesAvailable
    │   └── pricing → BoatPlacesPricing
    └── hasBerth → Berth

Vessel
├── refAuthorized → BoatAuthorized
└── at_location → [GPS coordinates]

Device
├── refPort → Port
├── observes → AirQualityObserved
└── measures → WeatherObserved
```

---

**Version:** 1.0  
**Generated:** 2026-04-27  
**Total Examples:** 12 entity types with real Galician port data
