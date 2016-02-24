-- DROP TABLE IF EXISTS nass.censusdata_0;
-- 
-- CREATE TABLE nass.censusdata_0
-- ( 
--   source_desc text,
--   sector_desc text,
--   group_desc text,
--   commodity_desc text,
--   class_desc text,
--   prodn_practice_desc text,
--   util_practice_desc text,
--   statisticcat_desc text,
--   unit_desc text,
--   short_desc text,
--   domain_desc text,
--   domaincat_desc text,
--   agg_level_desc text,
--   state_ansi integer,
--   state_fips_code integer,
--   state_alpha text,
--   state_name text,
--   asd_code integer,
--   asd_desc text,
--   counti_ansi integer,
--   county_code integer,
--   county_name text,
--   region_desc text,
--   zip_5 integer,
--   watershed_code integer,
--   watershed_desc text,
--   congr_district_code text,
--   country_code integer,
--   country_name text,
--   location_desc text,
--   year integer,
--   freq_desc text,
--   begin_code integer,
--   end_code integer,
--   reference_period_desc text,
--   week_ending date,
--   load_time date,
--   value text,
--   cv_pct text);

-- DROP TABLE IF EXISTS nass.censusdata;
-- SELECT source_desc, sector_desc, group_desc, commodity_desc, class_desc, 
-- 	prodn_practice_desc, util_practice_desc, statisticcat_desc, unit_desc, 
-- 	short_desc, domain_desc, domaincat_desc, agg_level_desc, state_ansi, 
-- 	state_fips_code, state_alpha, state_name, asd_code, asd_desc, 
-- 	counti_ansi, county_code, county_name, region_desc, zip_5, 
-- 	watershed_code, watershed_desc, congr_district_code, country_code, 
-- 	country_name, location_desc, year, freq_desc, begin_code, end_code, 
-- 	reference_period_desc, week_ending, load_time, cv_pct, value AS value_txt, 
-- 	NULLIF (regexp_replace(value, '[A-Za-z._%-\(\)\/\-,[:space:]]', '', 'gi'), '')::numeric  AS value
-- 
-- INTO nass.censusdata	
-- FROM nass.censusdata_0

DROP TABLE IF EXISTS nass.censusdata;

