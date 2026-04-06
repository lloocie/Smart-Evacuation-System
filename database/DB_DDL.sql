-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server|  Physical Implementation
-- ================================================================

USE SmartEvacuationDB;
GO

-- ================================================================
--  DROP TABLES (reverse order to respect foreign keys)
-- ================================================================

DROP TABLE IF EXISTS EDGE;
DROP TABLE IF EXISTS NODE;
DROP TABLE IF EXISTS ROUTE_STEP;
DROP TABLE IF EXISTS EVACUATION_ROUTE;
DROP TABLE IF EXISTS INCIDENT;
DROP TABLE IF EXISTS USER_LOCATION;
DROP TABLE IF EXISTS EMPLOYEE;
DROP TABLE IF EXISTS USER_ACCOUNT;
DROP TABLE IF EXISTS STAIRCASE_FLOOR;
DROP TABLE IF EXISTS STAIRCASE;
DROP TABLE IF EXISTS EXIT_POINT;
DROP TABLE IF EXISTS BEACON;
DROP TABLE IF EXISTS ZONE;
DROP TABLE IF EXISTS FLOOR;
DROP TABLE IF EXISTS BUILDING;
GO


-- ================================================================
-- CHAPTER 2 : DDL - TABLE CREATION
-- ================================================================

-- Table 1: BUILDING
CREATE TABLE BUILDING (
    building_id    INT           NOT NULL IDENTITY(1,1),
    building_name  VARCHAR(150)  NOT NULL,
    address        VARCHAR(255)  NOT NULL,
    building_type  VARCHAR(80)   NOT NULL,
    total_floors   INT           NOT NULL,
    CONSTRAINT pk_building         PRIMARY KEY (building_id),
    CONSTRAINT chk_building_floors CHECK (total_floors > 0)
);
GO

-- Table 2: FLOOR
CREATE TABLE FLOOR (
    floor_id       INT           NOT NULL IDENTITY(1,1),
    building_id    INT           NOT NULL,
    floor_number   INT           NOT NULL,
    map_reference  VARCHAR(120)  NULL,
    height_meters  DECIMAL(5,2)  NULL,
    CONSTRAINT pk_floor          PRIMARY KEY (floor_id),
    CONSTRAINT fk_floor_building FOREIGN KEY (building_id) REFERENCES BUILDING(building_id),
    CONSTRAINT uq_floor_per_bldg UNIQUE (building_id, floor_number)
);
GO

-- Table 3: ZONE
CREATE TABLE ZONE (
    zone_id    INT           NOT NULL IDENTITY(1,1),
    floor_id   INT           NOT NULL,
    zone_name  VARCHAR(120)  NOT NULL,
    zone_type  VARCHAR(80)   NOT NULL,
    CONSTRAINT pk_zone       PRIMARY KEY (zone_id),
    CONSTRAINT fk_zone_floor FOREIGN KEY (floor_id) REFERENCES FLOOR(floor_id)
);
GO

-- Table 4: BEACON
CREATE TABLE BEACON (
    beacon_id    INT           NOT NULL IDENTITY(1,1),
    floor_id     INT           NOT NULL,
    zone_id      INT           NULL,
    uuid         VARCHAR(36)   NOT NULL,
    major_value  INT           NOT NULL,
    minor_value  INT           NOT NULL,
    install_date DATE          NOT NULL,
    status       VARCHAR(10)   NOT NULL DEFAULT 'active',
    CONSTRAINT pk_beacon      PRIMARY KEY (beacon_id),
    CONSTRAINT fk_bcn_floor   FOREIGN KEY (floor_id) REFERENCES FLOOR(floor_id),
    CONSTRAINT fk_bcn_zone    FOREIGN KEY (zone_id)  REFERENCES ZONE(zone_id),
    CONSTRAINT uq_beacon_uuid UNIQUE (uuid),
    CONSTRAINT chk_beacon_status CHECK (status IN ('active','inactive'))
);
GO

-- Table 5: EXIT_POINT
CREATE TABLE EXIT_POINT (
    exit_id            INT           NOT NULL IDENTITY(1,1),
    floor_id           INT           NOT NULL,
    zone_id            INT           NULL,
    exit_name          VARCHAR(120)  NOT NULL,
    exit_type          VARCHAR(80)   NOT NULL,
    is_emergency_exit  BIT           NOT NULL DEFAULT 0,
    status             VARCHAR(10)   NOT NULL DEFAULT 'available',
    CONSTRAINT pk_exit       PRIMARY KEY (exit_id),
    CONSTRAINT fk_exit_floor FOREIGN KEY (floor_id) REFERENCES FLOOR(floor_id),
    CONSTRAINT fk_exit_zone  FOREIGN KEY (zone_id)  REFERENCES ZONE(zone_id),
    CONSTRAINT chk_exit_status CHECK (status IN ('available','blocked'))
);
GO

-- Table 6: STAIRCASE
CREATE TABLE STAIRCASE (
    staircase_id   INT           NOT NULL IDENTITY(1,1),
    building_id    INT           NOT NULL,
    staircase_name VARCHAR(120)  NOT NULL,
    type           VARCHAR(80)   NOT NULL,
    CONSTRAINT pk_staircase      PRIMARY KEY (staircase_id),
    CONSTRAINT fk_stair_building FOREIGN KEY (building_id) REFERENCES BUILDING(building_id)
);
GO

-- Table 7: STAIRCASE_FLOOR (Junction)
CREATE TABLE STAIRCASE_FLOOR (
    staircase_id  INT  NOT NULL,
    floor_id      INT  NOT NULL,
    CONSTRAINT pk_sf       PRIMARY KEY (staircase_id, floor_id),
    CONSTRAINT fk_sf_stair FOREIGN KEY (staircase_id) REFERENCES STAIRCASE(staircase_id),
    CONSTRAINT fk_sf_floor FOREIGN KEY (floor_id)     REFERENCES FLOOR(floor_id)
);
GO

-- Table 8: USER_ACCOUNT
CREATE TABLE USER_ACCOUNT (
    user_id      INT           NOT NULL IDENTITY(1,1),
    full_name    VARCHAR(150)  NOT NULL,
    phone        VARCHAR(20)   NULL,
    email        VARCHAR(150)  NOT NULL,
    role         VARCHAR(10)   NOT NULL DEFAULT 'occupant',
    company_name VARCHAR(150)  NULL,
    CONSTRAINT pk_user       PRIMARY KEY (user_id),
    CONSTRAINT uq_user_email UNIQUE (email),
    CONSTRAINT chk_user_role CHECK (role IN ('admin','occupant'))
);
GO

-- Table 9: EMPLOYEE
CREATE TABLE EMPLOYEE (
    employee_id  INT            NOT NULL IDENTITY(1,1),
    user_id      INT            NOT NULL,
    building_id  INT            NOT NULL,
    zone_id      INT            NULL,
    job_title    VARCHAR(100)   NOT NULL,
    department   VARCHAR(100)   NOT NULL,
    work_place   VARCHAR(150)   NULL,
    shift_start  TIME           NULL,
    shift_end    TIME           NULL,
    hire_date    DATE           NOT NULL,
    salary       DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    status       VARCHAR(10)    NOT NULL DEFAULT 'active',
    CONSTRAINT pk_employee     PRIMARY KEY (employee_id),
    CONSTRAINT uq_emp_user     UNIQUE (user_id),
    CONSTRAINT fk_emp_user     FOREIGN KEY (user_id)     REFERENCES USER_ACCOUNT(user_id),
    CONSTRAINT fk_emp_building FOREIGN KEY (building_id) REFERENCES BUILDING(building_id),
    CONSTRAINT fk_emp_zone     FOREIGN KEY (zone_id)     REFERENCES ZONE(zone_id),
    CONSTRAINT chk_emp_salary  CHECK (salary >= 0),
    CONSTRAINT chk_emp_status  CHECK (status IN ('active','inactive'))
);
GO

-- Table 10: USER_LOCATION
CREATE TABLE USER_LOCATION (
    location_id  INT       NOT NULL IDENTITY(1,1),
    user_id      INT       NOT NULL,
    beacon_id    INT       NOT NULL,
    floor_id     INT       NOT NULL,
    zone_id      INT       NULL,
    detected_at  DATETIME  NOT NULL DEFAULT GETDATE(),
    CONSTRAINT pk_location  PRIMARY KEY (location_id),
    CONSTRAINT fk_loc_user  FOREIGN KEY (user_id)   REFERENCES USER_ACCOUNT(user_id),
    CONSTRAINT fk_loc_bcn   FOREIGN KEY (beacon_id) REFERENCES BEACON(beacon_id),
    CONSTRAINT fk_loc_floor FOREIGN KEY (floor_id)  REFERENCES FLOOR(floor_id),
    CONSTRAINT fk_loc_zone  FOREIGN KEY (zone_id)   REFERENCES ZONE(zone_id)
);
GO

-- Table 11: INCIDENT
CREATE TABLE INCIDENT (
    incident_id    INT           NOT NULL IDENTITY(1,1),
    building_id    INT           NOT NULL,
    incident_type  VARCHAR(80)   NOT NULL,
    severity_level VARCHAR(10)   NOT NULL,
    start_time     DATETIME      NOT NULL,
    end_time       DATETIME      NULL,
    status         VARCHAR(10)   NOT NULL DEFAULT 'active',
    description    NVARCHAR(MAX) NULL,
    CONSTRAINT pk_incident        PRIMARY KEY (incident_id),
    CONSTRAINT fk_inc_building    FOREIGN KEY (building_id) REFERENCES BUILDING(building_id),
    CONSTRAINT chk_incident_times CHECK (end_time IS NULL OR end_time > start_time),
    CONSTRAINT chk_inc_severity   CHECK (severity_level IN ('low','medium','high','critical')),
    CONSTRAINT chk_inc_status     CHECK (status IN ('active','resolved'))
);
GO

-- Table 12: EVACUATION_ROUTE
CREATE TABLE EVACUATION_ROUTE (
    route_id            INT       NOT NULL IDENTITY(1,1),
    incident_id         INT       NOT NULL,
    user_id             INT       NOT NULL,
    start_floor_id      INT       NOT NULL,
    destination_exit_id INT       NOT NULL,
    created_at          DATETIME  NOT NULL DEFAULT GETDATE(),
    route_status        VARCHAR(10) NOT NULL DEFAULT 'generated',
    CONSTRAINT pk_route    PRIMARY KEY (route_id),
    CONSTRAINT fk_rt_inc   FOREIGN KEY (incident_id)         REFERENCES INCIDENT(incident_id),
    CONSTRAINT fk_rt_user  FOREIGN KEY (user_id)             REFERENCES USER_ACCOUNT(user_id),
    CONSTRAINT fk_rt_floor FOREIGN KEY (start_floor_id)      REFERENCES FLOOR(floor_id),
    CONSTRAINT fk_rt_exit  FOREIGN KEY (destination_exit_id) REFERENCES EXIT_POINT(exit_id),
    CONSTRAINT chk_route_status CHECK (route_status IN ('generated','completed','abandoned'))
);
GO

-- Table 13: ROUTE_STEP
CREATE TABLE ROUTE_STEP (
    step_id          INT   NOT NULL IDENTITY(1,1),
    route_id         INT   NOT NULL,
    step_number      INT   NOT NULL,
    floor_id         INT   NOT NULL,
    zone_id          INT   NULL,
    instruction_text NVARCHAR(MAX) NOT NULL,
    CONSTRAINT pk_step       PRIMARY KEY (step_id),
    CONSTRAINT uq_step_order UNIQUE (route_id, step_number),
    CONSTRAINT fk_step_route FOREIGN KEY (route_id) REFERENCES EVACUATION_ROUTE(route_id),
    CONSTRAINT fk_step_floor FOREIGN KEY (floor_id) REFERENCES FLOOR(floor_id),
    CONSTRAINT fk_step_zone  FOREIGN KEY (zone_id)  REFERENCES ZONE(zone_id)
);
GO

-- Table 14: NODE
CREATE TABLE NODE (
    node_id   INT           NOT NULL IDENTITY(1,1),
    floor_id  INT           NOT NULL,
    node_type VARCHAR(60)   NOT NULL,
    CONSTRAINT pk_node       PRIMARY KEY (node_id),
    CONSTRAINT fk_node_floor FOREIGN KEY (floor_id) REFERENCES FLOOR(floor_id)
);
GO

-- Table 15: EDGE
CREATE TABLE EDGE (
    edge_id   INT           NOT NULL IDENTITY(1,1),
    from_node INT           NOT NULL,
    to_node   INT           NOT NULL,
    distance  DECIMAL(8,2)  NOT NULL,
    CONSTRAINT pk_edge       PRIMARY KEY (edge_id),
    CONSTRAINT fk_edge_from  FOREIGN KEY (from_node) REFERENCES NODE(node_id),
    CONSTRAINT fk_edge_to    FOREIGN KEY (to_node)   REFERENCES NODE(node_id),
    CONSTRAINT chk_edge_dist CHECK (distance > 0)
);
GO
