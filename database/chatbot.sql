-- Create database
CREATE DATABASE SupportChatbot;
GO

USE SupportChatbot;
GO

-- Create Users table
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100),
    Email NVARCHAR(255),
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- Create Categories table
CREATE TABLE Categories (
    CategoryID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(50) NOT NULL,
    Team NVARCHAR(50) NOT NULL, -- Product/Billing/Tech/General
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- Create Tickets table
CREATE TABLE Tickets (
    TicketID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT FOREIGN KEY REFERENCES Users(UserID),
    CategoryID INT FOREIGN KEY REFERENCES Categories(CategoryID),
    Subject NVARCHAR(255) NOT NULL,
    Status NVARCHAR(20) DEFAULT 'open', -- open, in-progress, closed
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- Create Messages table
CREATE TABLE Messages (
    MessageID INT IDENTITY(1,1) PRIMARY KEY,
    TicketID INT FOREIGN KEY REFERENCES Tickets(TicketID),
    SenderID INT FOREIGN KEY REFERENCES Users(UserID), -- can be null for system messages
    Content NTEXT NOT NULL,
    IsAdminReply BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- Create CommonQueries table for instant solutions
CREATE TABLE CommonQueries (
    QueryID INT IDENTITY(1,1) PRIMARY KEY,
    CategoryID INT FOREIGN KEY REFERENCES Categories(CategoryID),
    Question NVARCHAR(255) NOT NULL,
    Solution NTEXT NOT NULL,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- Insert default categories
INSERT INTO Categories (Name, Team) VALUES
    ('Payments', 'Billing'),
    ('Product Issues', 'Product'),
    ('Technical Glitches', 'Tech'),
    ('General Inquiries', 'General');

-- Insert some common queries with solutions
INSERT INTO CommonQueries (CategoryID, Question, Solution) VALUES
    (1, 'How do I update my payment method?', 'You can update your payment method by going to Settings > Billing > Payment Methods and clicking "Add New Method".'),
    (1, 'When will I be charged?', 'Billing occurs on the first of each month for monthly plans. Annual plans are billed on your subscription anniversary date.'),
    (2, 'Product features not working', 'Please try clearing your browser cache and refreshing the page. If the issue persists, try logging out and back in.'),
    (3, 'Cannot login to account', 'First, ensure your caps lock is off and you''re using the correct email address. If you still can''t login, use the "Forgot Password" link to reset your password.'),
    (4, 'How do I contact support?', 'You can contact our support team through this chat interface or by sending an email to support@example.com');
GO
