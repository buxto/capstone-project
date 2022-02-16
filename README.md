# capstone-project

We compare the performances of stocks in different industries to economic data about those industries and to different cryptocurrencies; furthermore, we make predictions and investment recommendations to a mock client. A more detailed summary can be found in [project-specifications/ProjectExecutiveSummary.pdf](project-specifications/ProjectExecutiveSummary.pdf).

### Data Sources

We obtained real-time and historical data on stocks and cryptocurrencies from [Alpha Vantage](https://www.alphavantage.co/documentation/) and [Finnhub](https://finnhub.io/docs/api) APIs. We also obtained economic data from [https://data.census.gov/cedsci/table?q=ECNNAPCSIND2017.EC1700NAPCSINDPRD](https://data.census.gov/cedsci/table?q=ECNNAPCSIND2017.EC1700NAPCSINDPRD).

### Final Products

- The [dashboard](dashboard) folder simply contains a link to our dashboard, which can be found at [https://g3dash.herokuapp.com/](https://g3dash.herokuapp.com/)
- The written report is in [ProjectExecutiveReport.pdf](ProjectExecutiveReport.pdf)
- The presentation is in [CapstonePresentationSlides.pdf](CapstonePresentationSlides.pdf)

### Code

The [code](code) folder contains:

- The [DDL script](code/db_create.sql) to create our SQL database
- The machine learning models, as well as the Jupyter notebooks that generate them
- The source code for our dashboard (contained in [main.py](code/main.py))

### Other Files

The [project planning](project-planning) folder contains the [exploratory questions](project-planning/ExploratoryQuestions.pdf) we came up with at the start of the project, as well as the link to our [project management plan](https://trello.com/b/xMwenGs2/capstone-project-managment-plan).

The [project specifications](project-specifications) folder contains:
- An [ERD](project-specifications/ERD.pdf) for our SQL database
- Napkin drawings of our [visualizations](project-specifications/VisualizationsNapkinsAndFeedback.pdf) and our [dashboard layout](project-specifications/DashboardNapkinsAndFeedback.pdf)
- An [ETL report](project-specifications/RepeatableETLReport.pdf)
- A service diagram for our data pipelines (contained in [Data Platform.pdf](project-specifications/Data%20Platform.pdf))
- The [project summary](project-specifications/ProjectExecutiveSummary.pdf)

### Technologies Used

- Azure services (including Databricks, Data Factory, and SQL databases)
- Kafka
- Python (including Pandas, Plotly, and Dash)
- Jupyter Notebooks

### Group Members

- [Connor Buxton](https://www.linkedin.com/in/connor-buxton-748103181/)
- [Ben Hines](https://www.linkedin.com/in/ben-hines-426286225/)
- [Sargis Abrahamyan](https://www.linkedin.com/in/sargis-abrahamyan-1333571a0/)
- [Lucas Stefanic](https://www.linkedin.com/in/lucas-stefanic-661404212/)
