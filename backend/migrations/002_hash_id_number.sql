-- 迁移：将 students 表的 id_number 列替换为 id_number_hash
-- 注意：此操作不可逆。哈希是加盐 SHA-256，无法还原明文身份证号。
-- 执行前请先备份数据库！

-- 1. 添加 id_number_hash 列（允许 NULL，等下回填）
ALTER TABLE students ADD COLUMN IF NOT EXISTS id_number_hash VARCHAR(64);

-- 2. 确认迁移前的数据状态
DO $$
DECLARE
    row_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO row_count FROM students WHERE id_number IS NOT NULL AND id_number_hash IS NULL;
    RAISE NOTICE '待哈希行数: %', row_count;
END $$;

-- 3. 此步骤需要在应用层完成：用 Python 脚本逐行读取 id_number，
--    调用 hash_id_number() 计算哈希值，并 UPDATE 回对应行。
--    SQL 本身无法调用应用层的加盐哈希函数（SHA-256(salt + id_number)），
--    因此不能直接在 SQL 中批量计算。
--
--    请运行以下脚本完成哈希回填：
--      cd backend && uv run python scripts/hash_existing_id_numbers.py
--
--    或者：如果要放弃旧数据（仅适用于开发/测试环境），执行：
--      UPDATE students SET id_number_hash = '' WHERE id_number_hash IS NULL;

-- 4. 回填完成后，设置 NOT NULL 约束
-- ALTER TABLE students ALTER COLUMN id_number_hash SET NOT NULL;

-- 5. 删除旧列（确认所有功能正常后再执行）
-- ALTER TABLE students DROP COLUMN IF EXISTS id_number;
