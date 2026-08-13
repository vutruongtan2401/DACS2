IF DB_ID(N'TravelPlanner') IS NULL
BEGIN
    CREATE DATABASE [TravelPlanner];
END
GO

USE [TravelPlanner];
GO

DROP TABLE IF EXISTS [dbo].[itineraries];
DROP TABLE IF EXISTS [dbo].[users];
GO

CREATE TABLE [dbo].[users] (
    [id] INT IDENTITY(1,1) NOT NULL,
    [full_name] NVARCHAR(255) NOT NULL,
    [email] NVARCHAR(255) NOT NULL,
    [password_hash] NVARCHAR(255) NOT NULL,
    [phone] NVARCHAR(20) NULL,
    [address] NVARCHAR(500) NULL,
    [avatar_url] NVARCHAR(500) NULL,
    [role] NVARCHAR(20) NOT NULL CONSTRAINT [DF_users_role] DEFAULT N'USER',
    [status] NVARCHAR(20) NOT NULL CONSTRAINT [DF_users_status] DEFAULT N'ACTIVE',
    [created_at] DATETIME2(0) NOT NULL CONSTRAINT [DF_users_created_at] DEFAULT SYSDATETIME(),
    [updated_at] DATETIME2(0) NOT NULL CONSTRAINT [DF_users_updated_at] DEFAULT SYSDATETIME(),
    [last_login_at] DATETIME2(0) NULL,
    CONSTRAINT [PK_users] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [UQ_users_email] UNIQUE ([email]),
    CONSTRAINT [CK_users_role] CHECK ([role] IN (N'USER', N'ADMIN')),
    CONSTRAINT [CK_users_status] CHECK ([status] IN (N'ACTIVE', N'LOCKED', N'INACTIVE'))
);
GO

CREATE TABLE [dbo].[itineraries] (
    [id] INT IDENTITY(1,1) NOT NULL,
    [user_id] INT NOT NULL,
    [destination] NVARCHAR(255) NOT NULL,
    [start_date] DATE NOT NULL,
    [end_date] DATE NOT NULL,
    [spent_amount] FLOAT NOT NULL,
    [created_at] DATETIME2(0) NOT NULL CONSTRAINT [DF_itineraries_created_at] DEFAULT SYSDATETIME(),
    [updated_at] DATETIME2(0) NOT NULL CONSTRAINT [DF_itineraries_updated_at] DEFAULT SYSDATETIME(),
    CONSTRAINT [PK_itineraries] PRIMARY KEY CLUSTERED ([id]),
    CONSTRAINT [FK_itineraries_users] FOREIGN KEY ([user_id]) REFERENCES [dbo].[users] ([id]) ON DELETE CASCADE,
    CONSTRAINT [CK_itineraries_dates] CHECK ([end_date] >= [start_date]),
    CONSTRAINT [CK_itineraries_spent_amount] CHECK ([spent_amount] >= 0)
);
GO

CREATE INDEX [IX_itineraries_user_id] ON [dbo].[itineraries] ([user_id]);
CREATE INDEX [IX_itineraries_destination] ON [dbo].[itineraries] ([destination]);
GO
