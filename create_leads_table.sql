CREATE TABLE IF NOT EXISTS `leads` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(191) NOT NULL,
  `telefone` VARCHAR(50) DEFAULT NULL,
  `email` VARCHAR(191) DEFAULT NULL,
  `mensagem` TEXT DEFAULT NULL,
  `canal` ENUM('whatsapp','email','formulario') NOT NULL DEFAULT 'formulario',
  `pagina_origem` VARCHAR(255) DEFAULT NULL,
  `consentimento_lgpd` TINYINT(1) NOT NULL DEFAULT 0,
  `data_criacao` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_canal` (`canal`),
  INDEX `idx_data_criacao` (`data_criacao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
