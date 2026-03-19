-- Smart Service Finder - Database Schema
-- Run: mysql -u root < schema.sql

CREATE DATABASE IF NOT EXISTS smart_service_finder;
USE smart_service_finder;

-- Services table
CREATE TABLE IF NOT EXISTS services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category ENUM('hospital', 'food', 'repair', 'grocery') NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    address VARCHAR(500) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    rating DECIMAL(2, 1) DEFAULT 0.0,
    open_time TIME NOT NULL DEFAULT '08:00:00',
    close_time TIME NOT NULL DEFAULT '22:00:00',
    is_emergency BOOLEAN DEFAULT FALSE,
    crowd_level ENUM('low', 'medium', 'high') DEFAULT 'medium',
    wait_time INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    rating DECIMAL(2, 1) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- =====================
-- SEED DATA
-- =====================

-- Hospitals (Mumbai area coordinates ~19.076, 72.877)
INSERT INTO services (name, category, latitude, longitude, address, phone, rating, open_time, close_time, is_emergency) VALUES
('City General Hospital', 'hospital', 19.0760, 72.8777, '123 Marine Drive, Mumbai', '+91-22-2345-6789', 4.5, '00:00:00', '23:59:59', TRUE),
('LifeCare Medical Center', 'hospital', 19.0820, 72.8820, '45 Linking Road, Bandra', '+91-22-2678-1234', 4.2, '00:00:00', '23:59:59', TRUE),
('Sunrise Hospital', 'hospital', 19.0650, 72.8650, '78 Colaba Causeway, Colaba', '+91-22-2890-5678', 4.8, '00:00:00', '23:59:59', TRUE),
('MedPlus Clinic', 'hospital', 19.0900, 72.8900, '12 Andheri Station Rd', '+91-22-2456-7890', 3.9, '08:00:00', '22:00:00', FALSE);

-- Food
INSERT INTO services (name, category, latitude, longitude, address, phone, rating, open_time, close_time, is_emergency) VALUES
('Spice Garden Restaurant', 'food', 19.0780, 72.8790, '56 FC Road, Dadar', '+91-22-3456-7890', 4.6, '10:00:00', '23:00:00', FALSE),
('Quick Bites Cafe', 'food', 19.0740, 72.8760, '89 Hill Road, Bandra', '+91-22-3567-8901', 4.1, '07:00:00', '22:00:00', FALSE),
('Mumbai Tiffins', 'food', 19.0810, 72.8810, '34 SV Road, Andheri', '+91-22-3678-9012', 4.4, '06:00:00', '21:00:00', FALSE),
('Royal Biryani House', 'food', 19.0700, 72.8700, '67 Mohammed Ali Rd', '+91-22-3789-0123', 4.7, '11:00:00', '23:30:00', FALSE);

-- Repair
INSERT INTO services (name, category, latitude, longitude, address, phone, rating, open_time, close_time, is_emergency) VALUES
('FixIt Electronics', 'repair', 19.0770, 72.8780, '23 Lamington Rd, Grant Rd', '+91-22-4567-8901', 4.3, '09:00:00', '20:00:00', FALSE),
('AutoCare Garage', 'repair', 19.0850, 72.8850, '45 LBS Marg, Kurla', '+91-22-4678-9012', 4.0, '08:00:00', '19:00:00', FALSE),
('QuickFix Mobile Repairs', 'repair', 19.0730, 72.8750, '12 Linking Rd, Khar', '+91-22-4789-0123', 4.5, '10:00:00', '21:00:00', FALSE);

-- Grocery
INSERT INTO services (name, category, latitude, longitude, address, phone, rating, open_time, close_time, is_emergency) VALUES
('FreshMart Supermarket', 'grocery', 19.0790, 72.8800, '78 Turner Rd, Bandra', '+91-22-5678-9012', 4.4, '07:00:00', '22:00:00', FALSE),
('Daily Needs Store', 'grocery', 19.0720, 72.8730, '34 Peddar Rd, Breach Candy', '+91-22-5789-0123', 4.1, '06:00:00', '23:00:00', FALSE),
('Green Basket Organics', 'grocery', 19.0880, 72.8880, '56 Juhu Tara Rd, Juhu', '+91-22-5890-1234', 4.6, '08:00:00', '21:00:00', FALSE);

-- Sample reviews
INSERT INTO reviews (service_id, rating, comment) VALUES
(1, 5.0, 'Excellent emergency care, very responsive staff'),
(1, 4.0, 'Good facilities but long wait times'),
(3, 5.0, 'Best hospital in the area, top-notch doctors'),
(5, 4.5, 'Amazing food and great ambiance'),
(5, 4.0, 'Good variety but a bit pricey'),
(8, 5.0, 'Best biryani in Mumbai, must try!'),
(9, 4.0, 'Fixed my laptop quickly and reasonably priced'),
(12, 4.5, 'Fresh vegetables and great selection');
