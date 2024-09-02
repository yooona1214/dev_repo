# robot_data_agent
# 24.08.29

그래프 DB 생성 및 LLM 사용 방법
아래 sandbox.neo4j.com 링크 접속 후, 아래 cypher 쿼리 예시를 활용하여 그래프DB 생성 가능
해당 그래프 DB의 접속주소를 반영하여 LLM에서 활용가능(neo4j_test.py참조)

# 그래프DB 설정
neo4j sandbox : https://sandbox.neo4j.com/onboarding?_gl=1*1q39ncu*_gcl_au*MTY3MTgzODU4MS4xNzIwNTkwMTAy*_ga*MTUzNzg2MTI4OS4xNzIwNTkwMTAy*_ga_DL38Q8KGQC*MTcyNDgwMzU1NS4xNS4xLjE3MjQ4MDM5MTMuMC4wLjA.*_ga_DZP8Z65KK4*MTcyNDgwMzU1NS4xNi4xLjE3MjQ4MDM5MTMuMC4wLjA.


# 생성된 모든 Graph 시각화/조회하는 cypher query 예시
MATCH (n)-[r]-(m)
RETURN n, r, m


# 그래프DB "노드" 생성을 위한 Cypher query 예시
// Robot 노드 생성
CREATE (:Robot {robotID: 'R1', model: 'ModelX', manufacturer: 'CompanyA'});

// Service 노드 생성
CREATE (:Service {serviceID: 'S1', robotID: 'R1', serviceType: 'Maintenance', startTime: '2024-08-01T10:00:00', endTime: '2024-08-01T12:00:00', currentState: 'Completed'});

// ServiceStatus 노드 생성
CREATE (:ServiceStatus {serviceID: 'S1', timestamp: '2024-08-01T10:05:00', stateType: 'Start', stateValue: 'Initiated'});

// ServiceHistory 노드 생성
CREATE (:ServiceHistory {serviceID: 'S1', startTime: '2024-08-01T10:00:00', endTime: '2024-08-01T12:00:00', completionStatus: 'Success', destination: 'LocationA'});

// Error 노드 생성
CREATE (:Error {errorCode: 'E101', location: 'Arm', cause: 'Overheat', solution: 'Cool Down', threshold: '80C'});

// ErrorHistory 노드 생성
CREATE (:ErrorHistory {errorID: 'EH1', robotID: 'R1', timestamp: '2024-08-01T11:00:00', errorCode: 'E101'});

// State 노드 생성
CREATE (:State {stateID: 'ST1', robotID: 'R1', timestamp: '2024-08-01T11:30:00', stateType: 'Battery', stateValue: 'Low', threshold: '20%'});

// HardwareStatus 노드 생성
CREATE (:HardwareStatus {hardwareID: 'H1', robotID: 'R1', timestamp: '2024-08-01T11:45:00', hardwareType: 'UIPad', state: 'Operational'});

// SensorStatus 노드 생성
CREATE (:SensorStatus {sensorID: 'S1', robotID: 'R1', timestamp: '2024-08-01T11:50:00', sensorType: 'LiDAR', state: 'Active'});

// VoC 노드 생성
CREATE (:VoC {vocID: 'V1', majorCategory: 'Performance', minorCategory: 'Speed', customerComplaint: 'Slow response', cause: 'Software Lag', solution: 'Update Firmware', timestamp: '2024-08-01T12:00:00', robotID: 'R1', customerID: 'C1'});

// Customer 노드 생성
CREATE (:Customer {customerID: 'C1', name: 'John Doe', contact: '123-456-7890', address: '123 Main St', membershipLevel: 'Gold', joinDate: '2022-01-01', preferredContactMethod: 'Email'});


# 그래프DB "관계" 생성을 위한 Cypher query
// Robot - (has) -> Service 관계 생성
MATCH (r:Robot {robotID: 'R1'}), (s:Service {serviceID: 'S1'})
CREATE (r)-[:HAS_SERVICE]->(s);

// Service - (has) -> ServiceStatus 관계 생성
MATCH (s:Service {serviceID: 'S1'}), (ss:ServiceStatus {serviceID: 'S1'})
CREATE (s)-[:HAS_STATUS]->(ss);

// Service - (recorded) -> ServiceHistory 관계 생성
MATCH (s:Service {serviceID: 'S1'}), (sh:ServiceHistory {serviceID: 'S1'})
CREATE (s)-[:RECORDED_IN]->(sh);

// Error - (recorded) -> ErrorHistory 관계 생성
MATCH (e:Error {errorCode: 'E101'}), (eh:ErrorHistory {errorCode: 'E101'})
CREATE (e)-[:RECORDED_IN]->(eh);

// Robot - (has) -> State 관계 생성
MATCH (r:Robot {robotID: 'R1'}), (st:State {stateID: 'ST1'})
CREATE (r)-[:HAS_STATE]->(st);

// Robot - (has) -> HardwareStatus 관계 생성
MATCH (r:Robot {robotID: 'R1'}), (hs:HardwareStatus {hardwareID: 'H1'})
CREATE (r)-[:HAS_HARDWARE_STATUS]->(hs);

// Robot - (has) -> SensorStatus 관계 생성
MATCH (r:Robot {robotID: 'R1'}), (ss:SensorStatus {sensorID: 'S1'})
CREATE (r)-[:HAS_SENSOR_STATUS]->(ss);

// Robot - (has) -> VoC 관계 생성
MATCH (r:Robot {robotID: 'R1'}), (v:VoC {vocID: 'V1'})
CREATE (r)-[:HAS_VOC]->(v);

// Customer - (filed) -> VoC 관계 생성
MATCH (c:Customer {customerID: 'C1'}), (v:VoC {vocID: 'V1'})
CREATE (c)-[:FILED]->(v);
