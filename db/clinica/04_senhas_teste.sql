-- =====================================================================
-- clinica_db — senha dos veterinários de teste (FICTÍCIOS) (P1)
-- Os 3 veterinários de 02_dados_teste.sql têm hash fictício, que não entra
-- no login. Aqui eles recebem o hash bcrypt da senha "Senha@123".
-- Nenhum outro dado é alterado. Roda depois do 02_dados_teste.sql.
--   ana@clinica.com     -> ativa e com senha confirmada (entra)
--   carlos@clinica.com  -> inativo (bloqueado, teste 2)
--   beatriz@clinica.com -> senha não confirmada (bloqueada, teste 3)
-- =====================================================================

UPDATE veterinario
SET senha_hash = '$2b$12$dxiSBv2o11ls6X/9eOmLp.cqlQ7y6ppRxK7Hh1ehPKIUngryZQDNu'
WHERE email IN ('ana@clinica.com', 'carlos@clinica.com', 'beatriz@clinica.com');
