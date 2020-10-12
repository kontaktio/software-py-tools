select coalesce(e.email, i.email) as email,
       coalesce(e.empty, 0)       as empty_datahost,
       coalesce(i.incorrect, 0)   as incorrect_datahost
from (select m.email,
             count(m.email) as empty
      from device
               join manager m on device.manager_id = m.id
      where model = 'PORTAL_LIGHT'
        and (applications -> 'system' ->> 'dataHost' = '')
      group by email) e
         full outer join
     (
         select m.email,
                count(m.email) as incorrect
         from device
                  join manager m on device.manager_id = m.id
         where model = 'PORTAL_LIGHT'
           and (applications -> 'system' ->> 'dataHost' not in
                ('https://event-processor.prod.kontakt.io', 'https://gateway-proxy.kontakt.io', ''))
         group by email
     ) i on e.email = i.email
order by empty_datahost desc;