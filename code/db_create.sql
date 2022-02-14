USE group3-DB;
GO

CREATE TABLE Census
(
    Census_Data_ID INT PRIMARY KEY,
    NAICS_Code VARCHAR(max) NOT NULL,
    NAICS_Code_Meaning VARCHAR(max) NOT NULL,
    Number_of_Establishments VARCHAR(max) NOT NULL,
    Sales_Shipment_or_Revenue VARCHAR(max) NOT NULL
);

CREATE TABLE Real_Time_Stock
(
    RT_Stock_ID INT PRIMARY KEY,
    Ticker VARCHAR(max) NOT NULL,
    Open_P Float,
    Current_P Float,
    Low Float,
    High Float,
    Change Float,
    Per_Change Float,
    Time_t date,
);


CREATE TABLE Historical_Crypto
(
    HT_Crypto_ID INT PRIMARY KEY,
    Currency VARCHAR(max) NOT NULL,
    Open_P Float,
    Low Float,
    High Float,
    Close_P Float,
    Volume Float,
    Date_T date,
    Merket_Cap FLOAT
);

CREATE TABLE Historical_Stock
(
    HT_Stock_ID INT PRIMARY KEY,
    Ticker VARCHAR(max) NOT NULL,
    Open_P Float,
    Low Float,
    High Float,
    Volume Float,
    Time_t date,
    Close_P Float,
);


