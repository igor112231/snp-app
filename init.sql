CREATE DATABASE IF NOT EXISTS snp;
USE snp;

CREATE TABLE IF NOT EXISTS rna_pdist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    wildTypeSequence TEXT,
    mutantSequence TEXT,
    result VARCHAR(255),
    analysis_status ENUM('inProgress', 'finished')
);

-- echo -e "ACGUACGU\nUGCAUGCA" | RNApdist

--CREATE TABLE IF NOT EXISTS rna_fold (
--    id INT AUTO_INCREMENT PRIMARY KEY,
--    wildTypeSequence TEXT,
--    mutantSequence TEXT,
--    result VARCHAR(255),
--    analysis_status ENUM('inProgress', 'finished')
--);

-- echo "ACGUACGU" | RNAfold
-- echo "UGCAUGCA" | RNAfold

