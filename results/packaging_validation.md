# Packaging verification, 7 October 2026

- Downloaded the compressed historical dataset; its uncompressed SHA-256 matches the source dataset.
- 279,936 unique experiment keys and eight controllers with 34,992 runs each.
- All archived published mean columns match recomputation within 0.000051 (four-decimal rounding tolerance).
- Twelve smoke simulations executed successfully with two workers; analysis completed.
- Reran one archived case per controller (eight one-hour cases): every output metric matches the raw record within 1e-12 tolerance.
- Full expected factorial key set exactly matches the raw records.
- Main simulation and runner compared with the post-run source snapshot: only a trailing blank line and portable import-path setup differ.
- Complete analysis command executed on the downloaded raw dataset.
- Elsevier LaTeX compiled with latexmk/BibTeX; 32 references. PDF text and table content checked. Raster page inspection was attempted but the image display service could not process the rendered output.

The full simulation was not rerun for packaging. Dataset verification and completion checks are additional analyses of archived runs. Source snapshot is post-run, not an immutable execution capture. Physical ride control and human interface evaluation remain outstanding.
