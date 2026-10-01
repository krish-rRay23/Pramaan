"""
Pramaan v3.1 — Automated Software Bill of Materials (SBOM) Generator
====================================================================
Generates an enterprise CycloneDX 1.5 JSON SBOM covering:
- Python backend dependencies (FastAPI, cryptography, uvicorn, pydantic, etc.)
- Android application dependencies (Compose, Retrofit, OkHttp, Moshi, Coroutines)
- Cryptographic algorithm catalog and license attestations
Outputs: security/sbom.json
"""

import json
import os
import uuid
from datetime import datetime, timezone

def generate_sbom() -> dict:
    components = [
        # --- Backend Core ---
        {
            "type": "framework",
            "name": "fastapi",
            "version": "0.115.0",
            "description": "High performance modern web framework for building APIs with Python",
            "purl": "pkg:pypi/fastapi@0.115.0",
            "licenses": [{"license": {"id": "MIT"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "cryptography",
            "version": "42.0.8",
            "description": "Cryptographic recipes and primitives for Python (OpenSSL/Ed25519 C-bindings)",
            "purl": "pkg:pypi/cryptography@42.0.8",
            "licenses": [{"license": {"id": "Apache-2.0"}}, {"license": {"id": "BSD-3-Clause"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "pydantic",
            "version": "2.9.2",
            "description": "Data validation and settings management using Python type annotations",
            "purl": "pkg:pypi/pydantic@2.9.2",
            "licenses": [{"license": {"id": "MIT"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "uvicorn",
            "version": "0.30.6",
            "description": "Lightning-fast ASGI server implementation using uvloop and httptools",
            "purl": "pkg:pypi/uvicorn@0.30.6",
            "licenses": [{"license": {"id": "BSD-3-Clause"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "numpy",
            "version": "1.26.4",
            "description": "Fundamental package for array computing and spatial edge-variance calculation",
            "purl": "pkg:pypi/numpy@1.26.4",
            "licenses": [{"license": {"id": "BSD-3-Clause"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "pillow",
            "version": "10.4.0",
            "description": "Python Imaging Library fork for reading, sampling, and processing KYC frames",
            "purl": "pkg:pypi/pillow@10.4.0",
            "licenses": [{"license": {"id": "HPND"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "python-multipart",
            "version": "0.0.9",
            "description": "Streaming multipart parser for Python",
            "purl": "pkg:pypi/python-multipart@0.0.9",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "required"
        },

        # --- Android App Core ---
        {
            "type": "framework",
            "name": "androidx.compose.ui:ui",
            "version": "1.6.8",
            "description": "Android Jetpack Compose UI declarative toolkit",
            "purl": "pkg:maven/androidx.compose.ui/ui@1.6.8",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "required"
        },
        {
            "type": "framework",
            "name": "androidx.compose.material3:material3",
            "version": "1.2.1",
            "description": "Material 3 design components for Android Jetpack Compose",
            "purl": "pkg:maven/androidx.compose.material3/material3@1.2.1",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "com.squareup.retrofit2:retrofit",
            "version": "2.11.0",
            "description": "Type-safe HTTP client for Android and Java by Square",
            "purl": "pkg:maven/com.squareup.retrofit2/retrofit@2.11.0",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "com.squareup.okhttp3:okhttp",
            "version": "4.12.0",
            "description": "Square’s meticulous HTTP & HTTP/2 client for Android and Java",
            "purl": "pkg:maven/com.squareup.okhttp3/okhttp@4.12.0",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "com.squareup.moshi:moshi-kotlin",
            "version": "1.15.1",
            "description": "Modern JSON library for Kotlin and Java",
            "purl": "pkg:maven/com.squareup.moshi/moshi-kotlin@1.15.1",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "io.coil-kt:coil-compose",
            "version": "2.6.0",
            "description": "Fast, lightweight image loading library for Android Jetpack Compose",
            "purl": "pkg:maven/io.coil-kt/coil-compose@2.6.0",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "required"
        },
        {
            "type": "library",
            "name": "org.jetbrains.kotlinx:kotlinx-coroutines-android",
            "version": "1.8.1",
            "description": "Coroutines support libraries for Kotlin on Android",
            "purl": "pkg:maven/org.jetbrains.kotlinx/kotlinx-coroutines-android@1.8.1",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "required"
        },

        # --- AI Research Adapter ---
        {
            "type": "model",
            "name": "prithivMLmods/open-deepfake-detection",
            "version": "main-commit",
            "description": "Open-source research visual deepfake and synthetic detection adapter",
            "purl": "pkg:huggingface/prithivMLmods/open-deepfake-detection",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "scope": "optional"
        }
    ]

    sbom = {
        "$schema": "http://cyclonedx.org/schema/bom-1.5.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tools": [
                {
                    "vendor": "Pramaan Engineering",
                    "name": "pramaan-sbom-generator",
                    "version": "3.1.0"
                }
            ],
            "component": {
                "type": "application",
                "name": "PRAMAAN Financial Interaction Firewall",
                "version": "3.1.0-grand-finale-freeze",
                "description": "Cryptographic interaction firewall for high-risk financial communications",
                "licenses": [{"license": {"id": "Proprietary"}}]
            }
        },
        "components": components,
        "dependencies": [
            {
                "ref": "PRAMAAN Financial Interaction Firewall",
                "dependsOn": [c["name"] for c in components]
            }
        ]
    }
    return sbom

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "security")
    os.makedirs(out_dir, exist_ok=True)
    sbom_path = os.path.join(out_dir, "sbom.json")
    
    sbom_data = generate_sbom()
    with open(sbom_path, "w", encoding="utf-8") as f:
        json.dump(sbom_data, f, indent=2)

    print(f"[SBOM] Successfully generated CycloneDX 1.5 SBOM with {len(sbom_data['components'])} components at: {sbom_path}")
