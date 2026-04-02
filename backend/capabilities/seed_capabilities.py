"""
Seeds the core capabilities into the DB.
Safe to run multiple times.

Usage:
    python -m backend.capabilities.seed_capabilities
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.database import init_db
from backend.db.crud import insert_capability, get_all_capabilities, insert_profile

CAPABILITIES = [
    {
        "name": "Remote Sensing",
        "description": (
            "Expertise in acquiring and processing data from airborne and spaceborne sensors, "
            "including synthetic aperture radar (SAR), electro-optical/infrared (EO/IR), "
            "hyperspectral imaging, and multispectral sensors. Applications include terrain "
            "mapping, change detection, target recognition, and environmental monitoring."
        ),
        "keywords": [
            "SAR", "synthetic aperture radar", "LiDAR", "hyperspectral", "multispectral",
            "satellite imagery", "EO/IR", "electro-optical", "infrared", "remote sensing",
            "aerial imaging", "radar", "spectral", "optical sensor", "geospatial",
            "earth observation", "UAV sensor", "drone imaging", "thermal imaging",
            "change detection", "target detection", "surveillance imagery",
        ],
    },
    {
        "name": "3D Point Clouds",
        "description": (
            "Deep expertise in 3D point cloud acquisition, processing, and analysis from "
            "LiDAR sensors and photogrammetric reconstruction. Includes mesh generation, "
            "surface reconstruction, volumetric analysis, SLAM-based localization, and "
            "machine learning methods for 3D scene understanding."
        ),
        "keywords": [
            "point cloud", "LiDAR", "photogrammetry", "mesh reconstruction", "voxelization",
            "SLAM", "3D reconstruction", "surface reconstruction", "3D mapping",
            "volumetric", "depth sensing", "structured light", "stereo vision",
            "3D scene understanding", "PointNet", "3D object detection", "terrain model",
            "digital elevation model", "DEM", "DSM", "ground segmentation",
            "canopy height model", "CHM", "tree segmentation", "crop structure"
        ],
    },
    {
        "name": "Edge Computing",
        "description": (
            "Experience deploying real-time machine learning and signal processing pipelines "
            "on resource-constrained hardware including FPGAs, embedded processors, and "
            "custom SoCs. Focus on low-latency inference, model compression, on-device AI, "
            "and power-efficient processing for field-deployable systems."
        ),
        "keywords": [
            "edge computing", "embedded systems", "FPGA", "low-latency", "on-device",
            "real-time processing", "edge AI", "edge inference", "IoT", "embedded AI",
            "model compression", "quantization", "pruning", "TensorRT", "OpenVINO",
            "Jetson", "microcontroller", "SoC", "power-efficient", "field-deployable",
            "resource-constrained", "autonomous system", "onboard processing",
        ],
    },
    {
        "name": "Forestry and Invasive Species Management",
        "description": (
            "Expertise in mapping and managing forest resources, monitoring invasive species, "
            "and analyzing forest structural metrics using remote sensing and machine learning."
        ),
        "keywords": [
            "forest inventory", "invasive species", "canopy mapping", "tree detection", 
            "biomass", "phenology", "species classification", "forestry", "silviculture", "forest", "forests", "timber"
        ],
    },
    {
        "name": "Precision Agriculture",
        "description": (
            "Advanced techniques for crop monitoring, yield prediction, and resource optimization "
            "using aerial data, soil sensors, and geospatial analytics."
        ),
        "keywords": [
            "crop monitoring", "yield prediction", "soil moisture", "NDVI", 
            "variable rate application", "drone scouting", "field mapping", "precision ag", "agriculture"
        ],
    },
    {
        "name": "Novel Camera and Sensor Systems",
        "description": (
            "Design and development of cutting-edge imaging hardware including specialized "
            "focal plane arrays, neuromorphic vision systems, and low-SWaP sensors."
        ),
        "keywords": [
            "focal plane array", "CMOS", "event camera", "neuromorphic sensor", 
            "low-SWaP camera", "sensor fusion", "optical design", "camera design"
        ],
    },
    {
        "name": "Hyperspectral and Hypertemporal Imaging",
        "description": (
            "Analysis of dense spectral and temporal data cubes to extract fine-grained "
            "material properties and monitor dynamic phenological or environmental changes."
        ),
        "keywords": [
            "hyperspectral", "hypertemporal", "spectral unmixing", "time-series imagery", 
            "phenological change", "VNIR", "SWIR", "continuous monitoring"
        ],
    },
    {
        "name": "GIS Software Development",
        "description": (
            "Creation of robust geographic information systems, spatial databases, and "
            "web mapping applications adhering to OGC standards."
        ),
        "keywords": [
            "GIS", "geospatial", "spatial analysis", "vector data", "raster processing", 
            "QGIS", "ArcGIS", "geodatabase", "OGC standards", "web mapping", "PostGIS"
        ],
    },
    {
        "name": "UAV/UAS and Drones",
        "description": (
            "Development, operation, and payload integration for unmanned aerial vehicles. "
            "Expertise in flight control, mission planning, swarming, and edge-native processing."
        ),
        "keywords": [
            "UAV", "UAS", "drone", "unmanned aerial vehicle", "swarm", "flight control",
            "drone payload", "mission planning", "sUAS", "aerial robotics", "quadcopter"
        ]
    },
    {
        "name": "On-Orbit Sensors",
        "description": (
            "Design and deployment of spaceborne hardware and optics, including "
            "CubeSat payloads, radiation-hardened components, and orbital imaging systems."
        ),
        "keywords": [
            "on-orbit", "spaceborne", "CubeSat", "satellite payload", "radiation-hardened",
            "optical payload", "STK", "LEO", "GEO", "space sensor"
        ]
    },
    {
        "name": "Computer Vision",
        "description": (
            "Advanced image and video analysis methods encompassing deep learning models "
            "for object detection, segmentation, tracking, and facial recognition."
        ),
        "keywords": [
            "computer vision", "CNN", "object detection", "image segmentation", "YOLO",
            "tracking", "facial recognition", "optical flow", "image processing", "pattern recognition"
        ]
    }
]

SPECTRAL_CAPABILITIES = [
    {
        "name": "Electro-Optical Imaging and Sensing",
        "description": "Design and analysis of advanced EO/IR sensor systems, including multispectral, hyperspectral, and temporal imaging technologies.",
        "keywords": ["electro-optical", "EO/IR", "sensor design", "multispectral", "hyperspectral", "temporal imaging", "spectral imaging", "optical sensing"]
    },
    {
        "name": "Geospatial Systems and Remote Sensing",
        "description": "Exploitation of remote sensing data through geospatial information systems, including atmospheric correction and advanced image processing.",
        "keywords": ["geospatial", "remote sensing", "atmospheric correction", "image processing", "GIS", "spectral unmixing", "end member analysis", "FLAASH", "QUAC"]
    },
    {
        "name": "Gas Dynamics and Signatures",
        "description": "Modeling and simulation of gas dynamics, exhaust plumes, and radiative transfer for signature prediction.",
        "keywords": ["gas dynamics", "signatures", "exhaust plume", "radiative transfer", "MODTRAN", "SOCRATES", "ARISTOTLE", "plume simulation"]
    },
    {
        "name": "Environment and Space Physics",
        "description": "Research in space physics, orbit determination, and environmental modeling for space-based and high-altitude systems.",
        "keywords": ["space physics", "orbit determination", "environmental modeling", "synthetic atmosphere", "high-altitude", "space weather"]
    },
    {
        "name": "Applied Material Science",
        "description": "Development of novel materials, nanoscience applications, and diagnostic instruments for chemical mapping and combustion.",
        "keywords": ["material science", "nanoscience", "spectrometer", "chemical mapping", "combustion diagnostic", "FASPEC", "TRACER"]
    },
    {
        "name": "Hypersonics and Aerothermodynamics",
        "description": "Advanced computational fluid dynamics (CFD), aero-thermo-mechanical simulation, and ablation modeling for hypersonic vehicles. Expertise in turbulent heat flux closure, fluid-thermal-structural interactions (FTSI), and time-accurate flowfield prediction across varying flight regimes.",
        "keywords": ["hypersonics", "aerothermodynamics", "CFD", "ablation", "turbulence", "conjugate heat transfer", "finite-rate chemistry", "US3D"]
    },
    {
        "name": "Physics-Informed Artificial Intelligence / Machine Learning",
        "description": "Application of deep learning and ensemble models constrained by physical governing equations. Expertise in training algorithms with high-fidelity synthetic data for target detection, anomaly recognition, and complex fluid modeling where empirical data is sparse.",
        "keywords": ["artificial intelligence", "machine learning", "neural networks", "physics-informed machine learning", "PIML", "target identification", "anomaly detection", "algorithm development"]
    },
    {
        "name": "Synthetic Data and Scene Generation (M&S)",
        "description": "Development of radiative transfer testbeds and high-fidelity scene simulators to train algorithms and evaluate sensor performance. Capabilities span complex 3D environments including littoral zones, oceanic states, and cluttered maneuvering target backgrounds.",
        "keywords": ["scene generation", "synthetic data", "modeling and simulation", "M&S", "digital holography", "radiative transfer", "sensor calibration", "MCScene", "MODTRAN"]
    },
    {
        "name": "Counter-UAS and Advanced Threat Tracking",
        "description": "Design of multi-dimensional sensor systems and algorithms for searching, detecting, and determining the intent of Unmanned Aerial Systems (UAS). Expertise in clutter suppression, day/night operation, and tracking in highly cluttered kinetic environments.",
        "keywords": ["Counter-UAS", "C-UAS", "target tracking", "moving target indication", "MTI", "drone detection", "event-based sensing", "clutter suppression"]
    },
    {
        "name": "Atmospheric Modeling and Space Weather",
        "description": "Characterization and forecasting of atmospheric and ionospheric phenomena impacting electro-magnetic propagation, civilian communications, and radar. Expertise in marine boundary layer modeling, sporadic E-layer density predictions, and environmental data fusion.",
        "keywords": ["atmospheric modeling", "space weather", "ionosphere", "Sporadic-E", "marine boundary layer", "environmental intelligence", "refraction modeling"]
    }
]

def seed() -> None:
    init_db()
    
    import sqlite3
    db_path = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "proposalpilot.db"))
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Rename Profile 1 to Cory Garms if it exists
    cur.execute("UPDATE profiles SET name = 'Cory Garms' WHERE id = 1")
    cur.execute("INSERT OR IGNORE INTO profiles (name) VALUES ('Cory Garms')")
    
    # Create Spectral Sciences profile
    cur.execute("INSERT OR IGNORE INTO profiles (name) VALUES ('Spectral Sciences')")
    conn.commit()
    
    cur.execute("SELECT id FROM profiles WHERE name = 'Spectral Sciences'")
    row = cur.fetchone()
    spectral_id = row[0] if row else 2
    conn.close()
    
    existing = {c["name"] for c in get_all_capabilities(profile_id=1)}
    seeded = 0
    for cap in CAPABILITIES:
        if cap["name"] not in existing:
            insert_capability(cap["name"], cap["description"], json.dumps(cap["keywords"]), profile_id=1)
            print(f"  Seeded (Cory Garms): {cap['name']} ({len(cap['keywords'])} keywords)")
            seeded += 1
        else:
            print(f"  Skipped (Cory Garms): {cap['name']}")
            
    existing_spectral = {c["name"] for c in get_all_capabilities(profile_id=spectral_id)}
    spectral_seeded = 0
    for cap in SPECTRAL_CAPABILITIES:
        if cap["name"] not in existing_spectral:
            insert_capability(cap["name"], cap["description"], json.dumps(cap["keywords"]), profile_id=spectral_id)
            print(f"  Seeded (Spectral Sciences): {cap['name']} ({len(cap['keywords'])} keywords)")
            spectral_seeded += 1
        else:
            print(f"  Skipped (Spectral Sciences): {cap['name']}")
            
    print(f"\nDone. {seeded} new capabilities seeded for Cory Garms, {spectral_seeded} for Spectral Sciences.")

if __name__ == "__main__":
    seed()
