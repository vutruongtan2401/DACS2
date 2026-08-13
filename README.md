# Personalized Travel Planner

Ung dung web lap ke hoach du lich va quan ly chuyen di.

## Cau hinh nhanh

1. Copy `.env.example` thanh `.env`.
2. Cai dependency tu `requirements.txt`.
3. Tao database `TravelPlanner` tren SQL Server 19 bang SSMS hoac chay `schema.sql`.
4. Cap nhat `DATABASE_URL` trong `.env`.
5. Chay ung dung bang `python run.py`.

## Ket noi SQL Server 19

Vi du SQL Server Express named pipe:

```text
mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC+Driver+17+for+SQL+Server%7D%3BSERVER%3Dnp%3A%5C%5C.%5Cpipe%5CMSSQL%24SQLEXPRESS%5Csql%5Cquery%3BDATABASE%3DTravelPlanner%3BTrusted_Connection%3Dyes%3BEncrypt%3Dno%3BTrustServerCertificate%3Dyes%3B
```

Neu instance khac `SQLEXPRESS`, thay phan `SERVER` theo ten instance trong SSMS.
