SELECT t0.`id`, t0.`bool_col`, t0.`tinyint_col`, t0.`smallint_col`,
       t0.`int_col`, t0.`bigint_col`, t0.`float_col`, t0.`double_col`,
       t0.`date_string_col`, t0.`string_col`, t0.`timestamp_col`,
       t0.`year`, t0.`month`
FROM (
  SELECT t1.*
  FROM functional_alltypes t1
  UNION DISTINCT
  SELECT t1.*
  FROM functional_alltypes t1
) t0