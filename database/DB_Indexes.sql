-- ================================================================
--  SMART EVACUATION NAVIGATION SYSTEM
--  SQL Server (T-SQL)  |  Physical Implementation
-- ================================================================

USE SmartEvacuationDB;
GO

-- CHAPTER 6 : INDEXES
-- ================================================================

CREATE INDEX idx_floor_building    ON FLOOR(building_id);
CREATE INDEX idx_zone_floor        ON ZONE(floor_id);
CREATE INDEX idx_beacon_floor      ON BEACON(floor_id);
CREATE INDEX idx_beacon_zone       ON BEACON(zone_id);
CREATE INDEX idx_beacon_status     ON BEACON(status);
CREATE INDEX idx_exit_floor        ON EXIT_POINT(floor_id);
CREATE INDEX idx_exit_status       ON EXIT_POINT(status);
CREATE INDEX idx_exit_emergency    ON EXIT_POINT(is_emergency_exit);
CREATE INDEX idx_incident_building ON INCIDENT(building_id);
CREATE INDEX idx_incident_status   ON INCIDENT(status);
CREATE INDEX idx_route_incident    ON EVACUATION_ROUTE(incident_id);
CREATE INDEX idx_route_user        ON EVACUATION_ROUTE(user_id);
CREATE INDEX idx_step_route        ON ROUTE_STEP(route_id);
CREATE INDEX idx_loc_user          ON USER_LOCATION(user_id);
CREATE INDEX idx_loc_time          ON USER_LOCATION(detected_at);
CREATE INDEX idx_edge_from         ON EDGE(from_node);
CREATE INDEX idx_edge_to           ON EDGE(to_node);
GO


-- ================================================================