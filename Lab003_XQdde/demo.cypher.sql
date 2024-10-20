MATCH (p:Project {name: 'Project AGD'})-[:INVOLVES]->(d:Document)
MATCH (p)-[:INVOLVES]->(e:Developer)
RETURN d.title, e.name


SELECT d.title, e.name
FROM Project p
JOIN Project_Document pd ON p.id = pd.project_id
JOIN Document d ON pd.document_id = d.id
JOIN Project_Developer pe ON p.id = pe.project_id
JOIN Developer e ON pe.dev_id = e.id
WHERE p.name = 'Project AGD';

