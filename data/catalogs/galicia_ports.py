# Galician Ports Real Catalog
# Real coordinates, administrative data, and operational characteristics

GALICIAN_PORTS = {
    "a-coruna": {
        "name": "Puerto de A Coruña",
        "coordinates": [-8.3936, 43.3613],
        "description": "Main port of A Coruña, northwest coast",
        "port_type": "SeaPort",
        "authority_name": "Autoridad Portuaria de A Coruña",
        "authority_contact": "info@puertocoruna.es",
        "authority_phone": "+34 981 22 27 00",
        "authority_website": "http://www.puertocoruna.es",
        "num_berths": 12,
        "main_facility": "Terminal General de A Coruña",
        "facility_capacity": 250
    },
    "vigo": {
        "name": "Puerto de Vigo",
        "coordinates": [-8.7670, 42.2362],
        "description": "Major commercial port in Pontevedra",
        "port_type": "SeaPort",
        "authority_name": "Autoridad Portuaria de Vigo",
        "authority_contact": "info@pvigo.es",
        "authority_phone": "+34 986 20 02 00",
        "authority_website": "http://www.pvigo.es",
        "num_berths": 15,
        "main_facility": "Terminal Multipropósito de Vigo",
        "facility_capacity": 300
    },
    "ferrol": {
        "name": "Puerto de Ferrol",
        "coordinates": [-8.2444, 43.4667],
        "description": "Naval and commercial port in Ferrol",
        "port_type": "SeaPort",
        "authority_name": "Autoridad Portuaria de Ferrol-San Cibrao",
        "authority_contact": "info@puertferrol.es",
        "authority_phone": "+34 981 38 14 00",
        "authority_website": "http://www.puertferrol.es",
        "num_berths": 10,
        "main_facility": "Terminal Naval de Ferrol",
        "facility_capacity": 200
    },
    "marin": {
        "name": "Puerto de Marín",
        "coordinates": [-8.7033, 42.3967],
        "description": "Small port in Pontevedra, Ría de Pontevedra",
        "port_type": "SeaPort",
        "authority_name": "Autoridad Portuaria de Marín",
        "authority_contact": "info@puerto.marin.es",
        "authority_phone": "+34 986 92 01 85",
        "authority_website": "http://www.puerto.marin.es",
        "num_berths": 6,
        "main_facility": "Instalación Principal de Marín",
        "facility_capacity": 100
    },
    "vilagarcia": {
        "name": "Puerto de Vilagarcía de Arousa",
        "coordinates": [-8.7681, 42.6153],
        "description": "Commercial and fishing port in Arousa Bay",
        "port_type": "SeaPort",
        "authority_name": "Autoridad Portuaria de Vilagarcía",
        "authority_contact": "info@puerto.vilagarcia.es",
        "authority_phone": "+34 986 50 80 01",
        "authority_website": "http://www.puerto.vilagarcia.es",
        "num_berths": 8,
        "main_facility": "Terminal de Carga Vilagarcía",
        "facility_capacity": 150
    },
    "ribeira": {
        "name": "Puerto de Ribeira",
        "coordinates": [-9.2717, 42.5544],
        "description": "Fishing port on Arousa Bay coast",
        "port_type": "SeaPort",
        "authority_name": "Autoridad Portuaria de Ribeira",
        "authority_contact": "info@puerto.ribeira.es",
        "authority_phone": "+34 981 82 19 50",
        "authority_website": "http://www.puerto.ribeira.es",
        "num_berths": 7,
        "main_facility": "Lonja y Muelles Ribeira",
        "facility_capacity": 120
    },
    "burela": {
        "name": "Puerto de Burela",
        "coordinates": [-7.5817, 43.3283],
        "description": "Fishing port in Lugo, north coast",
        "port_type": "SeaPort",
        "authority_name": "Autoridad Portuaria de Burela",
        "authority_contact": "info@puerto.burela.es",
        "authority_phone": "+34 982 58 02 14",
        "authority_website": "http://www.puerto.burela.es",
        "num_berths": 5,
        "main_facility": "Instalación Pesquera Burela",
        "facility_capacity": 80
    },
    "baiona": {
        "name": "Puerto de Baiona",
        "coordinates": [-8.8350, 42.1205],
        "description": "Historic port and recreational harbor",
        "port_type": "SeaPort",
        "authority_name": "Autoridad Portuaria de Baiona",
        "authority_contact": "info@puerto.baiona.es",
        "authority_phone": "+34 986 33 56 46",
        "authority_website": "http://www.puerto.baiona.es",
        "num_berths": 8,
        "main_facility": "Marina Recreativa Baiona",
        "facility_capacity": 100
    }
}


# Pricing categories based on ISO 8666 boat length classes
PRICING_CATEGORIES = {
    "A": {
        "name": "Small boats",
        "iso8266_length_min": 0,
        "iso8266_length_max": 7,
        "price_per_day": 45.0
    },
    "B": {
        "name": "Medium boats",
        "iso8266_length_min": 7,
        "iso8266_length_max": 12,
        "price_per_day": 75.0
    },
    "C": {
        "name": "Large boats",
        "iso8266_length_min": 12,
        "iso8266_length_max": 18,
        "price_per_day": 120.0
    },
    "D": {
        "name": "Extra large boats",
        "iso8266_length_min": 18,
        "iso8266_length_max": 25,
        "price_per_day": 180.0
    }
}


# Sample vessels (real-world inspired, fictional IMO/MMSI)
MASTER_VESSELS = [
    {
        "imo": "9876543",
        "name": "Galicia Trader",
        "ship_type": "General Cargo",
        "length": 120.5,
        "beam": 18.2,
        "depth": 10.5,
        "gross_tonnage": 8500,
        "net_tonnage": 5200,
        "year_built": 2010,
        "flag_state": "ES"
    },
    {
        "imo": "9876544",
        "name": "Ría Explorer",
        "ship_type": "Container Ship",
        "length": 185.0,
        "beam": 32.2,
        "depth": 15.0,
        "gross_tonnage": 35000,
        "net_tonnage": 19500,
        "year_built": 2015,
        "flag_state": "ES"
    },
    {
        "imo": "9876545",
        "name": "Pescador Gallego",
        "ship_type": "Fishing Vessel",
        "length": 65.0,
        "beam": 12.0,
        "depth": 7.0,
        "gross_tonnage": 1200,
        "net_tonnage": 600,
        "year_built": 2012,
        "flag_state": "ES"
    },
    {
        "imo": "9876546",
        "name": "Atlantic Star",
        "ship_type": "Bulk Carrier",
        "length": 190.0,
        "beam": 30.0,
        "depth": 14.5,
        "gross_tonnage": 40000,
        "net_tonnage": 22000,
        "year_built": 2008,
        "flag_state": "PT"
    },
    {
        "imo": "9876547",
        "name": "Coruña Express",
        "ship_type": "General Cargo",
        "length": 130.0,
        "beam": 19.5,
        "depth": 11.0,
        "gross_tonnage": 10000,
        "net_tonnage": 6000,
        "year_built": 2013,
        "flag_state": "ES"
    },
    {
        "imo": "9876548",
        "name": "Vigo Bridge",
        "ship_type": "Container Ship",
        "length": 200.0,
        "beam": 34.0,
        "depth": 16.0,
        "gross_tonnage": 45000,
        "net_tonnage": 25000,
        "year_built": 2018,
        "flag_state": "ES"
    },
    {
        "imo": "9876549",
        "name": "Ferrol Guardian",
        "ship_type": "Tanker",
        "length": 175.0,
        "beam": 28.0,
        "depth": 13.5,
        "gross_tonnage": 32000,
        "net_tonnage": 18000,
        "year_built": 2011,
        "flag_state": "ES"
    },
    {
        "imo": "9876550",
        "name": "Arousa Navigator",
        "ship_type": "General Cargo",
        "length": 110.0,
        "beam": 17.0,
        "depth": 9.5,
        "gross_tonnage": 6500,
        "net_tonnage": 3800,
        "year_built": 2014,
        "flag_state": "ES"
    },
    {
        "imo": "9876551",
        "name": "Marina del Mar",
        "ship_type": "Refrigerated Cargo",
        "length": 145.0,
        "beam": 21.0,
        "depth": 11.5,
        "gross_tonnage": 12000,
        "net_tonnage": 7000,
        "year_built": 2016,
        "flag_state": "ES"
    },
    {
        "imo": "9876552",
        "name": "Galicia Pride",
        "ship_type": "General Cargo",
        "length": 125.0,
        "beam": 18.5,
        "depth": 10.2,
        "gross_tonnage": 9000,
        "net_tonnage": 5200,
        "year_built": 2017,
        "flag_state": "ES"
    }
]


# Vessel instance data (vessels currently operating, linked to MasterVessel)
VESSEL_INSTANCES = [
    {
        "imo": "9876543",
        "mmsi": "224123456",
        "name": "Galicia Trader",
        "vessel_type": "General Cargo",
        "current_port": "a-coruna",
        "status": "in_port"
    },
    {
        "imo": "9876544",
        "mmsi": "224123457",
        "name": "Ría Explorer",
        "vessel_type": "Container Ship",
        "current_port": "vigo",
        "status": "in_port"
    },
    {
        "imo": "9876545",
        "mmsi": "224123458",
        "name": "Pescador Gallego",
        "vessel_type": "Fishing Vessel",
        "current_port": "ribeira",
        "status": "in_port"
    },
    {
        "imo": "9876546",
        "mmsi": "224123459",
        "name": "Atlantic Star",
        "vessel_type": "Bulk Carrier",
        "current_port": "ferrol",
        "status": "approaching"
    },
    {
        "imo": "9876547",
        "mmsi": "224123460",
        "name": "Coruña Express",
        "vessel_type": "General Cargo",
        "current_port": "a-coruna",
        "status": "departing"
    },
    {
        "imo": "9876548",
        "mmsi": "224123461",
        "name": "Vigo Bridge",
        "vessel_type": "Container Ship",
        "current_port": "vigo",
        "status": "at_anchorage"
    },
    {
        "imo": "9876549",
        "mmsi": "224123462",
        "name": "Ferrol Guardian",
        "vessel_type": "Tanker",
        "current_port": "ferrol",
        "status": "in_port"
    },
    {
        "imo": "9876550",
        "mmsi": "224123463",
        "name": "Arousa Navigator",
        "vessel_type": "General Cargo",
        "current_port": "vilagarcia",
        "status": "in_port"
    },
    {
        "imo": "9876551",
        "mmsi": "224123464",
        "name": "Marina del Mar",
        "vessel_type": "Refrigerated Cargo",
        "current_port": "marin",
        "status": "in_port"
    },
    {
        "imo": "9876552",
        "mmsi": "224123465",
        "name": "Galicia Pride",
        "vessel_type": "General Cargo",
        "current_port": "baiona",
        "status": "in_port"
    }
]


# Authorized boats (recreational/merchant authorization)
AUTHORIZED_BOATS = [
    {
        "es_code": "es-224123456",
        "mmsi": "224123456",
        "authorized_port": "a-coruna",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123457",
        "mmsi": "224123457",
        "authorized_port": "vigo",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123458",
        "mmsi": "224123458",
        "authorized_port": "ribeira",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123459",
        "mmsi": "224123459",
        "authorized_port": "ferrol",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123460",
        "mmsi": "224123460",
        "authorized_port": "a-coruna",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123461",
        "mmsi": "224123461",
        "authorized_port": "vigo",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123462",
        "mmsi": "224123462",
        "authorized_port": "ferrol",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123463",
        "mmsi": "224123463",
        "authorized_port": "vilagarcia",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123464",
        "mmsi": "224123464",
        "authorized_port": "marin",
        "authorization_type": "commercial"
    },
    {
        "es_code": "es-224123465",
        "mmsi": "224123465",
        "authorized_port": "baiona",
        "authorization_type": "commercial"
    }
]


# Sensor devices per port
SENSOR_DEVICES = {
    "a-coruna": [
        {
            "name": "Air Quality Monitor - A Coruña Port",
            "device_type": "AirQualityMeter",
            "coordinates": [-8.3936, 43.3613]
        },
        {
            "name": "Weather Station - A Coruña Port",
            "device_type": "WeatherStation",
            "coordinates": [-8.3936, 43.3613]
        }
    ],
    "vigo": [
        {
            "name": "Air Quality Monitor - Vigo Port",
            "device_type": "AirQualityMeter",
            "coordinates": [-8.7670, 42.2362]
        },
        {
            "name": "Weather Station - Vigo Port",
            "device_type": "WeatherStation",
            "coordinates": [-8.7670, 42.2362]
        }
    ],
    "ferrol": [
        {
            "name": "Air Quality Monitor - Ferrol Port",
            "device_type": "AirQualityMeter",
            "coordinates": [-8.2444, 43.4667]
        },
        {
            "name": "Weather Station - Ferrol Port",
            "device_type": "WeatherStation",
            "coordinates": [-8.2444, 43.4667]
        }
    ],
    "marin": [
        {
            "name": "Air Quality Monitor - Marín Port",
            "device_type": "AirQualityMeter",
            "coordinates": [-8.7033, 42.3967]
        }
    ],
    "vilagarcia": [
        {
            "name": "Air Quality Monitor - Vilagarcía Port",
            "device_type": "AirQualityMeter",
            "coordinates": [-8.7681, 42.6153]
        }
    ],
    "ribeira": [
        {
            "name": "Weather Station - Ribeira Port",
            "device_type": "WeatherStation",
            "coordinates": [-9.2717, 42.5544]
        }
    ],
    "burela": [
        {
            "name": "Air Quality Monitor - Burela Port",
            "device_type": "AirQualityMeter",
            "coordinates": [-7.5817, 43.3283]
        }
    ],
    "baiona": [
        {
            "name": "Weather Station - Baiona Port",
            "device_type": "WeatherStation",
            "coordinates": [-8.8350, 42.1205]
        }
    ]
}
