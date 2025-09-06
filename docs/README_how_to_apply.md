
# How to Apply This Patch Bundle

1) **Merge the patch bundle blocks** into your spec:
   - Open your main spec file and paste the contents of `econ_gaps_patch_bundle_2025-09-05_21-17-35.md` at appropriate locations.
   - Blocks are atomic and wrapped with `BEGIN/END` IDs.

2) **Apply bulk renames & cross-ref fixes**:
   - Use `econ_bulk_renames_2025-09-05_21-17-35.json` as instructions for your doc-bot or run simple find/replace:
     - Replace `@ECON.007.004` → `@ECON.007.003`
     - Replace `checksum` → `checksum_sha256` (only in CSV schemas/examples).

3) **Run the linter**:
   ```bash
   python econ_doc_lint.py /path/to/your/spec.md
   ```
   - It checks BEGIN/END pairing, cross-ref prefixes, and required CSV meta fields.

4) **Extend**:
   - Update `enum_registry` with your actual `symbol` universe and any additional enums.
   - Add more ACCEPTANCE tests as you refine flows.

Happy shipping!
