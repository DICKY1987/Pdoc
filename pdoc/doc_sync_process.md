# Document Synchronization Process

## 📋 Current Implementation

### **Patch Bundle Workflow**
```bash
# 1. Apply atomic patch blocks
cat econ_gaps_patch_bundle_2025-09-05_21-17-35.md >> your_spec.md

# 2. Apply bulk renames
python apply_bulk_renames.py econ_bulk_renames_2025-09-05_21-17-35.json

# 3. Validate integrity
python pdoc/econ_doc_lint.py your_spec.md
python scripts/validate_cross_refs.py
```

### **Validation Pipeline**
```bash
# Block integrity
python pdoc/econ_doc_lint.py spec.md
python pdoc/huey_doc_lint.py spec.md

# Cross-reference validation
python scripts/validate_cross_refs.py

# Test suite
pytest tests/test_*_lint.py
```

## 🎯 **Key Features Present**

### ✅ **Atomic Block Management**
- Structured BEGIN/END blocks with unique IDs
- Dependency tracking (`DEPS:`, `AFFECTS:`)
- Version-controlled patches

### ✅ **Cross-Reference Integrity**
- Master cross-reference matrix (`cross_refs.yml`)
- Automated validation of section links
- Shared definition enforcement

### ✅ **Bulk Operations**
- JSON-defined rename operations
- Consistent field name changes across documents
- Regex-based transformations

### ✅ **Validation Framework**
- Multiple linters for different document types
- Automated testing with pytest
- Checksum validation for CSV contracts

## 🚀 **Advanced Capabilities Designed**

### **Change Request Management**
From `doc_sync_solutions.md`:
- Impact analysis templates
- Synchronized review cycles
- Tracking branches for complex changes

### **Documentation Generation**
- Template-driven generation from schemas
- Enum registries with single source of truth
- API documentation from OpenAPI specs

### **CI/CD Integration** 
- GitHub Actions workflows for validation
- Automated cross-reference checking
- Change impact reporting

## 🔧 **Tools & Scripts**

| Tool | Purpose | Status |
|------|---------|---------|
| `econ_doc_lint.py` | Block integrity validation | ✅ Implemented |
| `huey_doc_lint.py` | HUEY-specific validation | ✅ Implemented |
| `validate_cross_refs.py` | Cross-reference checking | ✅ Implemented |
| Bulk rename scripts | Consistent field changes | ✅ JSON configs |
| Patch bundle system | Atomic updates | ✅ Working |
| Template generators | Schema-driven docs | 📋 Designed |
| Change request workflow | Review coordination | 📋 Designed |

## 💡 **Usage Examples**

### **Adding New Shared Schema**
```yaml
# Add to cross_refs.yml
new_concept:
  huey_p_section: "§X.Y"
  backend_section: "§X.Y" 
  description: "New shared concept"
  shared_definition: "schemas/new_concept.md"
```

### **Bulk Field Rename**
```json
{
  "edits": [
    {
      "kind": "field-rename",
      "search": "old_field",
      "replace": "new_field",
      "scope_hint": "CSV schemas only"
    }
  ]
}
```

### **Atomic Block Update**
```markdown
<!-- BEGIN:ECON.XXX.YYY.ZZZ.TYPE.name -->
New content here
<!-- DEPS: ECON.AAA.BBB -->
<!-- AFFECTS: ECON.CCC.DDD -->
<!-- END:ECON.XXX.YYY.ZZZ.TYPE.name -->
```

## 🎯 **Benefits Achieved**

1. **Consistency** - Shared schemas prevent drift
2. **Traceability** - Dependencies tracked explicitly  
3. **Automation** - Validation prevents errors
4. **Scalability** - Structured blocks enable tooling
5. **Maintainability** - Cross-references stay valid