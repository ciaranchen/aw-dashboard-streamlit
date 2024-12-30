create view if not exists view_events as
select events.id,
       events.starttime,
       events.endtime,
       events.bucketrow,
--        events.endtime - events.starttime        as duration,
       buckets.name,
       buckets.hostname,
       buckets.type,
       buckets.client,
       events.data,
       json_extract(events.data, '$.app')       as data_app,
       json_extract(events.data, '$.title')     as data_title,
       json_extract(events.data, '$.status')    as data_status,
       json_extract(events.data, '$.audible')   as data_audible,
       json_extract(events.data, '$.incognito') as data_incognito,
       json_extract(events.data, '$.tabCount')  as data_tabCount,
--        json_extract(events.data, '$.title')     as data_title,
       json_extract(events.data, '$.url')       as data_url,
       json_extract(events.data, '$.file')      as data_file,
       json_extract(events.data, '$.language')  as data_language,
       json_extract(events.data, '$.project')   as data_project
from events
         INNER JOIN buckets ON events.bucketrow = buckets.id;