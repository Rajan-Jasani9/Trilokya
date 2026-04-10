"""
Seed script for DRDO Technology domains.
Creates predefined technology categories and writes SVG placeholder files to media/technologies/.
Icons shown in the app come from frontend/src/assets (see technologyAssets.js); filenames stay in DB for slug alignment.

Run from repo backend folder using the project venv, e.g.:
  .\\venv\\Scripts\\python.exe scripts\\init_technologies.py
  (or scripts\\run_init_technologies.bat)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.technology import Technology

SCRIPT_DIR = Path(__file__).parent
MEDIA_DIR = SCRIPT_DIR.parent / "media" / "technologies"

# Single placeholder; UI uses bundled PNGs from the frontend.
GENERIC_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="10" y="10" width="44" height="44" rx="8"/><path d="M22 32h20M32 22v20"/></svg>'
)


def _slugify(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[&/]", "_and_", slug)
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug


def _icon_stem(name: str) -> str:
    """Stem must match keys in frontend/src/utils/technologyAssets.js (see TECHNOLOGY_IMAGE_BY_SLUG)."""
    return ICON_STEM_OVERRIDES.get(name, _slugify(name))


# Only where display name would not produce the same stem as the frontend map expects.
ICON_STEM_OVERRIDES: dict[str, str] = {}


# (display name, short description) — order is display_order 1..N
TECH_DATA = [
    ("Additive Manufacturing", "3D printing and additive processes for defense hardware and tooling."),
    ("Aero Structures", "Aircraft and vehicle structural design, analysis, and qualification."),
    ("Aerodynamics", "Flow physics, wind tunnel correlation, and flight vehicle aerodynamic design."),
    ("Aeromechanical Systems", "Rotating machinery, aeroelasticity, and mechanical integration for air platforms."),
    (
        "Agro Technology for Military Support in High Altitude Areas",
        "Agricultural and environmental technologies for sustainment in extreme terrain.",
    ),
    ("AI/ML Technology", "Artificial intelligence and machine learning for sensing, autonomy, and decision support."),
    ("Alternative Power Plant", "Non-traditional power generation for vehicles, bases, and field systems."),
    ("Antennas", "Antenna design for radar, communications, navigation, and EW."),
    ("Armoured & Combat Vehicles", "Protection, mobility, and lethality for land combat platforms."),
    ("Autonomous Systems and Robotics", "Unmanned ground, air, and robotic systems for defense missions."),
    ("Behavioural Analysis for Soldiers", "Human performance, cognitive load, and behavioral assessment."),
    ("Bio Defence", "Biological threat detection, protection, and decontamination."),
    ("Bio Remediation", "Environmental bioremediation and ecological restoration."),
    ("Biomedical Engineering & Technologies", "Medical devices, diagnostics, and soldier health monitoring."),
    ("C4ISR", "Command, control, communications, computers, intelligence, surveillance, and reconnaissance."),
    ("Camouflage Technology", "Visual, IR, and multispectral concealment and signature management."),
    ("CBRN Defence", "Chemical, biological, radiological, and nuclear detection and protection."),
    ("Communication", "Tactical and strategic voice, data, and satellite communications."),
    ("Control Systems", "Guidance, navigation, flight control, and closed-loop platform control."),
    ("Counter Swarm Technology", "Detection and defeat of drone swarms and massed low-cost threats."),
    (
        "Cyber, Information & Communication Security",
        "Cyber defense, information assurance, and secure communications.",
    ),
    ("Decoys", "Expendable decoys and diversion for missiles and sensors."),
    ("Detonics & Mechanisms", "Fuzing, initiation, and energetic mechanisms."),
    ("Diesel Engine", "Compression-ignition engines for land and naval platforms."),
    ("Electric Power Technology", "Power electronics, distribution, and electric propulsion."),
    ("Electro Optics", "EO/IR sensors, lasers, and imaging for targeting and surveillance."),
    ("Electronic Devices", "Semiconductors, microelectronics, and ruggedized electronics."),
    ("Electronic Warfare", "Electronic attack, protection, and support measures."),
    ("EM Rail Gun", "Electromagnetic launch and directed-energy concepts."),
    ("Embedded Systems", "Real-time firmware, SoCs, and embedded computing."),
    ("Energy", "Energy storage, generation, and efficiency for defense systems."),
    ("Environment Protection", "Pollution control, habitat protection, and compliance."),
    ("Environmental Testing", "Climatic, shock, vibration, and qualification testing."),
    ("Fire Fighting", "Fire suppression, rescue, and safety for facilities and platforms."),
    ("Guidance & Navigation", "INS/GNSS, seekers, and navigation algorithms."),
    ("Guided Artillery", "Precision artillery, guided rounds, and fire control."),
    ("Gun Technology", "Small and large caliber guns, ammunition, and ballistics."),
    ("Hardware In Loop Simulation", "HIL rigs for real-time system and software validation."),
    ("High Performance Computing", "HPC clusters, solvers, and large-scale simulation."),
    ("Hydro Structures", "Hydraulic structures, dams, and water-related civil engineering."),
    ("Hypersonic Technologies", "Hypersonic flight, thermal protection, and propulsion."),
    ("Life Support", "Crew and soldier life support, environmental control, and safety."),
    ("Materials", "Advanced materials, composites, and process development."),
    ("Military Food Technology", "Rations, preservation, and nutrition for deployed forces."),
    ("Mines & Mines Detection", "Land and sea mines, clearance, and detection systems."),
    ("Missile Systems", "Missile airframes, propulsion, and system integration."),
    ("Multi-Barrel Rockets", "Rocket artillery, launchers, and area fires."),
    ("Munition/Ammunition", "Ammunition families, fuzes, and terminal effects."),
    ("Natural Hazard Management", "Earthquake, flood, and disaster mitigation for infrastructure."),
    ("Non Destructive Evaluation", "NDT/NDE for quality assurance and in-service inspection."),
    ("Ocean Profiling", "Oceanographic sensors, bathymetry, and water-column characterization."),
    ("Parachute Technology", "Personnel and cargo parachutes and aerial delivery."),
    ("Passive Countermeasures", "Chaff, flares, and passive signature reduction."),
    ("Propulsion Technologies", "Jet, rocket, and hybrid propulsion for air and missile systems."),
    ("Protective Clothing & Gears", "Ballistic and CBRN protective garments and equipment."),
    ("Quantum Technologies", "Quantum sensing, communication, and computing research."),
    ("Radar", "Surveillance, tracking, and fire-control radar systems."),
    ("Radome", "Electromagnetic windows and radomes for antennas and seekers."),
    ("Respiratory Management", "Breathing apparatus and respiratory protection."),
    ("Seeker", "RF, IR, and multimode seekers for guided weapons."),
    ("Sensors/Detectors", "General sensing, detectors, and measurement chains."),
    ("Soldier Support", "Load carriage, ergonomics, and dismounted soldier systems."),
    ("Sonar", "Underwater acoustics, sonar arrays, and ASW sensors."),
    ("Space Situational Awareness", "Space object tracking, conjunction, and debris awareness."),
    ("Space Technologies", "Satellites, launch, and space-borne payloads."),
    ("Surveillance and Tracking", "Persistent surveillance, target tracking, and situational awareness."),
    ("Swarm Technology", "Coordinated multi-agent UAS and swarm behaviors."),
    ("Terahertz", "THz imaging, spectroscopy, and communications research."),
    ("UAV", "Unmanned aerial vehicles and mission payloads."),
    ("UGV", "Unmanned ground vehicles and autonomy stacks."),
    ("Underwater Defence Technologies", "ASW, underwater sensors, and sub-surface defense."),
    ("Wargaming", "Simulation, exercises, and campaign analysis."),
    ("Warhead/Explosive & Ballistic Protection", "Warheads, blast, and ballistic protection engineering."),
    ("Waste Management", "Hazardous waste handling, treatment, and disposal."),
    ("Fibre Optics & Photonics", "Optical fiber links, photonic sensors, and ruggedized photonics."),
    ("Flight Sciences", "Flight testing, flight mechanics, and experimental aerodynamics."),
    ("Gas Turbine Engine", "Gas turbine cores, controls, and propulsion integration."),
    ("Life Sciences", "Biology, human factors, and life-science support to defense R&D."),
    ("Naval Systems", "Naval combat systems, platform integration, and maritime missions."),
    ("Night Vision Technology", "Image intensifiers, thermal fusion, and low-light systems."),
    ("Nuclear Technology", "Radiation detection, nuclear safety, and related instrumentation."),
    ("Simulation & Modelling", "Physics-based simulation, digital twins, and modelling workflows."),
    ("Stealth Technology", "Signature control, RCS, and low-observable engineering."),
    ("Textile & Special Materials", "Ballistic textiles, technical fabrics, and special materials."),
    ("Underwater Weapons", "Torpedoes, mines, and underwater ordnance engineering."),
    ("Microwave Technologies", "Microwave circuits, MMICs, and high-power microwave subsystems."),
    ("Explosives & Pyrotechnics", "Energetic materials, pyrotechnics, and safe handling."),
]

TECHNOLOGIES = [
    {
        "name": name,
        "description": desc,
        "display_order": idx + 1,
        "svg": GENERIC_SVG,
    }
    for idx, (name, desc) in enumerate(TECH_DATA)
]


def seed_technologies(db: Session):
    """Insert/update technology records; deactivate names not in the current catalog."""
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    new_names = {t["name"] for t in TECHNOLOGIES}
    stale = db.query(Technology).filter(~Technology.name.in_(new_names)).all()
    for row in stale:
        row.is_active = False
    if stale:
        print(f"  Deactivated {len(stale)} technologies not in the current catalog.")

    created = 0
    updated = 0

    for tech_data in TECHNOLOGIES:
        filename = _icon_stem(tech_data["name"]) + ".svg"
        svg_path = MEDIA_DIR / filename
        svg_path.write_text(tech_data["svg"], encoding="utf-8")

        existing = db.query(Technology).filter(Technology.name == tech_data["name"]).first()
        if existing:
            changed = False
            if existing.icon_filename != filename:
                existing.icon_filename = filename
                changed = True
            if existing.description != tech_data["description"]:
                existing.description = tech_data["description"]
                changed = True
            if existing.display_order != tech_data["display_order"]:
                existing.display_order = tech_data["display_order"]
                changed = True
            if not existing.is_active:
                existing.is_active = True
                changed = True
            if changed:
                updated += 1
                print(f"  [~] Updated: {tech_data['name']}")
            else:
                print(f"  [.] Up to date: {tech_data['name']}")
            continue

        tech = Technology(
            name=tech_data["name"],
            description=tech_data["description"],
            icon_filename=filename,
            is_active=True,
            display_order=tech_data["display_order"],
        )
        db.add(tech)
        created += 1
        print(f"  [+] Created: {tech_data['name']} ({filename})")

    db.commit()
    print(f"\n  Created: {created} | Updated: {updated} | Catalog size: {len(TECHNOLOGIES)}")
    print(f"  SVG placeholders written to: {MEDIA_DIR.resolve()}")


def main():
    print("=" * 60)
    print("DRDO Technologies - Seed Script")
    print("=" * 60)
    print()

    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        seed_technologies(db)
        print()
        print("[OK] Technology seeding completed!")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
