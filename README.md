Repairable Systems Visual Workbench

Overview

Repairable Systems Visual Workbench is an independent desktop application for exploratory reliability analysis of repairable systems. It provides a visual interface for entering failure data, fitting a Power Law Process model, generating diagnostic plots, and exporting statistical results.

This project is an independent software implementation based on public statistical methods for NHPP, Power Law Process modeling, and reliability growth analysis. It is not an official publication, endorsement, certification, or validated tool from any standards organization, publisher, or third party institution.

Main features

1. Visual data entry with spreadsheet style tables
2. Support for single item data, multiple items with a common observation horizon, multiple items with different observation horizons, and grouped interval data
3. Estimation of beta, lambda, and failure intensity z(t)
4. Cumulative failure plots, log log plots, QQ plots, TTT plots, and intensity plots
5. Bootstrap based confidence bands for model curves when enabled
6. Goodness of fit assessment using Cramer von Mises simulation
7. Export of plots and statistical summaries
8. Multilingual interface support

Mathematical core

The application implements the Power Law Process form

Lambda(t) = lambda t^beta

z(t) = lambda beta t^(beta minus 1)

The Cramer von Mises critical values are computed by Monte Carlo simulation at runtime. The program does not include reproduced critical value tables. In each simulation, ordered uniform samples are generated, the relative shape parameter is estimated again, the Cramer von Mises statistic is computed, and the requested quantile is used as the critical threshold.

Confidence limits for z(t) are computed from analytical approximations and bootstrap procedures, depending on the selected option. No embedded tabulations are used for these calculations.

Data examples

Embedded examples are synthetic and generated only for software demonstration. They are not copied from any protected publication or proprietary data source.

Project structure

run_workbench.py
    Main entry point used to start the application.

repairable_workbench/i18n.py
    Interface text, translations, labels, and language dictionaries.

repairable_workbench/math_core.py
    Statistical estimation, model fitting, goodness of fit calculations, confidence intervals, bootstrap routines, and Monte Carlo critical value generation.

repairable_workbench/results.py
    Result containers and formatted statistical summaries.

repairable_workbench/plotting.py
    Plot preparation utilities and model curve support.

repairable_workbench/resources.py
    Import, export, saving, synthetic examples, and auxiliary resources.

repairable_workbench/ui_components.py
    Reusable visual components, including spreadsheet style data tables.

repairable_workbench/visual.py
    Main graphical interface and application layout.

Installation

Python 3.10 or newer is recommended.

Install the required packages with

pip install numpy scipy matplotlib

Running the application

From the project folder, run

python run_workbench.py

Windows example

cd "C:\Users\Windows\Documents\Projects\modular_workbench_v3"
C:\Users\Windows\AppData\Local\Programs\Python\Python313\python.exe .\run_workbench.py

If the ZIP file creates a nested folder, enter the inner folder that contains run_workbench.py and the repairable_workbench directory before running the command.

Main recent change

The main file changed in this release is

repairable_workbench/math_core.py

The previous fixed table based Cramer von Mises threshold logic was replaced by Monte Carlo critical value generation.

Publication notes

This repository is intended as independent educational and engineering software. Before public release, avoid adding protected text, reproduced tables, screenshots, figures, logos, or examples copied from commercial standards, books, manuals, or proprietary internal reports.

Recommended repository names

repairable_systems_workbench
nhpp_reliability_workbench
power_law_process_workbench

Suggested short repository description

Independent visual workbench for repairable systems reliability analysis using NHPP and Power Law Process methods.

License

Add a license file before publishing the project. For public open source release, common options are MIT, BSD 3 Clause, Apache 2.0, or GPL 3.0, depending on how permissive you want the reuse terms to be.