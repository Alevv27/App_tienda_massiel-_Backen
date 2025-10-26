/* ===========================
   DB: MassielQA (SQL Server)
   Modela: Usuarios, Perfiles, Empresas,
           Credenciales y Módulos por perfil
   ===========================*/

IF DB_ID('MassielQA') IS NULL
BEGIN
    PRINT 'Creando BD MassielQA...';
    CREATE DATABASE MassielQA;
END
GO

USE MassielQA;
GO

/* Limpieza (idempotente para desarrollo) */
IF OBJECT_ID('dbo.PerfilModulo') IS NOT NULL DROP TABLE dbo.PerfilModulo;
IF OBJECT_ID('dbo.Credencial')   IS NOT NULL DROP TABLE dbo.Credencial;
IF OBJECT_ID('dbo.Usuario')      IS NOT NULL DROP TABLE dbo.Usuario;
IF OBJECT_ID('dbo.Perfil')       IS NOT NULL DROP TABLE dbo.Perfil;
IF OBJECT_ID('dbo.Modulo')       IS NOT NULL DROP TABLE dbo.Modulo;
IF OBJECT_ID('dbo.Empresa')      IS NOT NULL DROP TABLE dbo.Empresa;
GO

/* Tablas base */
CREATE TABLE dbo.Empresa(
    id           INT IDENTITY(1,1) PRIMARY KEY,
    nombre       NVARCHAR(120) NOT NULL
);

CREATE TABLE dbo.Perfil(
    id               INT IDENTITY(1,1) PRIMARY KEY,
    codigo           VARCHAR(20) UNIQUE NOT NULL,   -- ADMIN | GESTOR | FIRMANTE
    administracion   BIT NOT NULL DEFAULT 0,
    gestion          BIT NOT NULL DEFAULT 0,
    firmar           BIT NOT NULL DEFAULT 0
);

CREATE TABLE dbo.Usuario(
    id         INT IDENTITY(1,1) PRIMARY KEY,
    nombre     NVARCHAR(120) NOT NULL,
    email      VARCHAR(150)  NOT NULL UNIQUE,
    perfil_id  INT NOT NULL  FOREIGN KEY REFERENCES dbo.Perfil(id),
    empresa_id INT NOT NULL  FOREIGN KEY REFERENCES dbo.Empresa(id),
    activo     BIT NOT NULL DEFAULT 1
);

CREATE TABLE dbo.Credencial(
    usuario_id INT PRIMARY KEY FOREIGN KEY REFERENCES dbo.Usuario(id) ON DELETE CASCADE,
    -- Para demo dejamos texto plano; en prod usa HASH + SALT (p. ej., PBKDF2/argon2)
    password   VARCHAR(120) NOT NULL
);

/* Catálogo de módulos (para menú y control fino si luego crece) */
CREATE TABLE dbo.Modulo(
    id     INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,  -- ADMINISTRACION | GESTION | FIRMAR
    nombre NVARCHAR(120) NOT NULL
);

/* Relación Perfil-Modulo (permite granularidad futura) */
CREATE TABLE dbo.PerfilModulo(
    perfil_id INT NOT NULL FOREIGN KEY REFERENCES dbo.Perfil(id) ON DELETE CASCADE,
    modulo_id INT NOT NULL FOREIGN KEY REFERENCES dbo.Modulo(id) ON DELETE CASCADE,
    enabled   BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_PerfilModulo PRIMARY KEY (perfil_id, modulo_id)
);

/* Seed: Empresas */
INSERT INTO dbo.Empresa(nombre) VALUES (N'Empresa 1'), (N'Empresa 2');

/* Seed: Perfiles (mapea tu perfiles.json) */
INSERT INTO dbo.Perfil(codigo, administracion, gestion, firmar)
VALUES ('ADMIN',    1, 1, 1),
       ('GESTOR',   0, 1, 0),
       ('FIRMANTE', 0, 1, 1);

/* Seed: Módulos */
INSERT INTO dbo.Modulo(codigo, nombre)
VALUES ('ADMINISTRACION', N'Administración'),
       ('GESTION',        N'Gestión'),
       ('FIRMAR',         N'Firmar documentos');

/* Perfil ↔ Módulos (coherente con las banderas) */
INSERT INTO dbo.PerfilModulo(perfil_id, modulo_id, enabled)
SELECT p.id, m.id,
       CASE m.codigo
            WHEN 'ADMINISTRACION' THEN p.administracion
            WHEN 'GESTION'        THEN p.gestion
            WHEN 'FIRMAR'         THEN p.firmar
       END
FROM dbo.Perfil p
CROSS JOIN dbo.Modulo m;

/* Seed: Usuarios (mapea tu usuarios.json) */
DECLARE @pADMIN    INT = (SELECT id FROM dbo.Perfil WHERE codigo='ADMIN');
DECLARE @pGESTOR   INT = (SELECT id FROM dbo.Perfil WHERE codigo='GESTOR');
DECLARE @pFIRMANTE INT = (SELECT id FROM dbo.Perfil WHERE codigo='FIRMANTE');

INSERT INTO dbo.Usuario(nombre, email, perfil_id, empresa_id)
VALUES (N'Alejandro', 'ale@gmail.com',    @pADMIN,    1),
       (N'Marcelo',   'marcel@gmail.com', @pFIRMANTE, 1),
       (N'Cavero',    'cavero@gmail.com', @pGESTOR,   1),
       (N'Javier',    'jvnier@gmail.com', @pGESTOR,   2);

/* Credenciales (mapea tu auth.json) — DEMO SOLO */
INSERT INTO dbo.Credencial(usuario_id, password)
SELECT id, '123456' FROM dbo.Usuario;

/* Vista útil: menu por usuario (módulos habilitados) */
IF OBJECT_ID('dbo.v_MenuPorUsuario') IS NOT NULL DROP VIEW dbo.v_MenuPorUsuario;
GO
CREATE VIEW dbo.v_MenuPorUsuario AS
SELECT  u.id        AS usuario_id,
        u.email,
        p.codigo    AS perfil,
        STRING_AGG(m.codigo, ',') WITHIN GROUP (ORDER BY m.codigo) AS modulos
FROM dbo.Usuario u
JOIN dbo.Perfil p        ON p.id = u.perfil_id
JOIN dbo.PerfilModulo pm ON pm.perfil_id = p.id AND pm.enabled = 1
JOIN dbo.Modulo m        ON m.id = pm.modulo_id
GROUP BY u.id, u.email, p.codigo;
GO
