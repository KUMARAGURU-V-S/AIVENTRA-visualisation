# 3D Autopsy Visualization - AI Agent Integration Guide

This guide is for AI agents tasked with generating or modifying the `autopsy.json` file. The goal is to ensure that verbal descriptions in the autopsy report are correctly mapped to 3D markers on the skeleton model.

## 1. JSON Schema Requirement

The AI agent MUST output data in the following format:

```json
{
  "patient_id": "STRING",
  "report_date": "YYYY-MM-DD",
  "marks": [
    {
      "id": "UNIQUE_ID",
      "type": "fracture | injury | evidence | trauma",
      "location": "ANATOMICAL_NAME",
      "color": "CSS_COLOR_OR_HEX",
      "description": "DETAILED_DESCRIPTION"
    }
  ]
}
```

## 2. Anatomical Mapping Logic

The system uses **Semantic Anatomical Mapping**. The AI agent should use standard anatomical terms in the `location` field.

### Keywords for Sides
To place a marker on a specific side, include the words **"left"** or **"right"** in the `location` string.
- Example: `"left femur"` -> Places marker on the left thigh bone.
- Example: `"right rib"` -> Places marker on the right side of the ribcage.

### Supported Anatomical Terms
The agent should prefer these keywords which are pre-mapped to the 3D meshes:

| Verbal Term | Maps to Mesh Name (Internal) |
| :--- | :--- |
| **skull / head / frontal** | Frontal bone |
| **chest / sternum** | Body of sternum |
| **rib** | Rib (1st - 12th) |
| **spine / vertebrae / back** | Thoracic/Lumbar vertebrae |
| **neck / cervical** | Cervical vertebrae |
| **femur / upper leg** | Femur.r |
| **tibia / lower leg** | Tibia.r |
| **humerus / upper arm** | Humerus.r |
| **radius / forearm** | Radius.r |
| **ulna / forearm** | Ulna.r |
| **metacarpal / hand** | Metacarpal bones |
| **metatarsal / foot** | Metatarsal bones |
| **hip / pelvis** | Hip bone |

## 3. Best Practices for the AI Agent

1.  **Be Specific:** Instead of just "leg", use "left femur" or "right tibia".
2.  **Color Coding:** 
    - Use `red` for fractures.
    - Use `orange` or `purple` for soft tissue injuries/trauma.
    - Use `yellow` or `blue` for foreign evidence/objects.
3.  **Descriptions:** Write concise but medically accurate descriptions as they will appear in the UI sidebar and 3D tooltips.
4.  **Avoid Raw Coords:** The agent should **not** attempt to generate X, Y, Z coordinates unless it has access to the specific spatial grid of the model. Stick to the `location` field for robustness.

## 4. Integration Step
After generating the JSON, overwrite the contents of `public/autopsy.json` in the project root. The 3D viewer will automatically refresh and resolve the new locations.
