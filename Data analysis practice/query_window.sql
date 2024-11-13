#### На какую сумму делает покупки каждый клиент, в каждом рейтинговом сегменте,для каждого фильма,и сколько раз он совершает эту покупку.Так же,указана длина фильма,рейтинг и название.

select customer_id,
sum(amount) over choices ,
count(r.rental_id) over choices,
c.name as category,
length,rating,title
from inventory as i
join rental as r using(inventory_id) 
join payment as p using(customer_id)
join film as f using(film_id)
join film_category as fc using(film_id)
join category as c using(category_id)
window choices as (partition by customer_id,rating,title)

#### Какие фильмы продаются больше всего и меньше всего в разбиение по рейтингу.Так же,указана сумма уплаченная за взятие в аренду фильма,указан рейтинг и количество взятия в аренду опредленной рейтинговой группы.

select customer_id,
title,
first_value(title) over rate as popular,
last_value(title) over rate as unpopular,
count(r.rental_id) over rate,
amount,rating
from inventory as i
join rental as r using(inventory_id) 
join payment as p using(customer_id)
join film as f using(film_id)
window rate as (partition by rating order by amount desc)

#### На какое время обычно берут фильмы клиенты,сегментация клиентов с помощью квантилей по времени аренды.Так же,ууказано название фильма,рейтинг,категория фильма.

select customer_id,
extract(day from (return_date - rental_date)) as rental_period,
title,rating,c.name,
NTILE(3) OVER (PARTITION BY customer_id ORDER BY extract(day from (return_date - rental_date))) AS rental_period_quartile
from inventory as i
join rental as r using(inventory_id) 
join payment as p using(customer_id)
join film as f using(film_id)
join film_category as fc using(film_id)
join category as c using(category_id)

#### Создание единой витрины данных для визуализации. Выводит индентификатор клиента,сумму покупки,город,область,язык фильма,категория фильма,длина,рейтинговая категория,название,время аренды,фамилию сотрудника,год выпуска фильма,особенности фильма

with cus_add as (
select customer_id,amount,city,district,s.last_name,film_id,inventory_id
from address 
join city using(city_id)
join customer as cu using(address_id)
join inventory using(store_id)
join payment as p using(customer_id)
join staff as s using(staff_id)
)

select r.customer_id,amount,city,district,
c.name as category,length,rating,title,
extract(day from (return_date - rental_date)) as rental_period,
cad.last_name,l.name,release_year,special_features
from (select * from cus_add limit 100000) as cad
join film as f using(film_id)
join rental as r using(inventory_id)
join film_category as fc using(film_id)
join category as c using(category_id)
join language as l using(language_id)

#### Создание витрины данных для выявления сезонности в продажах по категориям. 
select name,amount,
extract(month from rental_date) as month_pay
from rental

join payment using(rental_id)
join inventory using(inventory_id)
join film_category using(film_id)
join category using(category_id)

#### Создание витрины данных для исследование какие актеры приносят больше прибыли,в каких городах какие актеры пользуются большей популярностью.(вложенный запрос с limit добавлен для оптимизации запроса,его можно исключить)

select a.last_name as actor,
sum(amount) over(partition by a.last_name) as profit,
first_value(city) over( partition by a.last_name order by amount desc) as popular_city
from (select * from payment limit 1000)
join customer using(customer_id)
join address using(address_id)
join city using(city_id)
join staff s using(staff_id)
join inventory i on s.store_id = i.store_id
join film_actor using(film_id)
join actor a using(actor_id)


### Пример запроса к другой базе данных,CTE упрощают жизнь.
with filtered_messages as (
    select
        *,
        to_timestamp(created_at) as created_time
    from test.chat_messages
),
message_with_blocks as (
    select
        message_id,
        created_by,
        entity_id,
        type,
        created_time,
        case
            when created_by = lag(created_by) over (partition by entity_id order by created_time) then null
            else 1
        end as new_block_flag
    from filtered_messages
),
message_blocks as (
    select
        message_id,
        created_by,
        entity_id,
        type,
        created_time,
        coalesce(sum(new_block_flag) over (partition by entity_id order by created_time rows between unbounded preceding and current row), 0) as block_id
    from message_with_blocks
),
client_messages as (
    select
        message_id,
        entity_id,
        created_time,
        block_id
    from message_blocks
    where type = 'incoming_chat_message'
),
manager_responses as (
    select
        cm.entity_id ,
        cm.message_id as client_message_id,
        mr.message_id as manager_message_id,
        cm.created_time as client_time,
        mr.created_time as manager_time,
        extract(epoch from (mr.created_time - cm.created_time)) / 60 as response_time_minutes,
        cm.block_id as client_block_id,
        mr.created_by as manager_id
    from client_messages as cm
    join message_blocks as mr on cm.entity_id = mr.entity_id and mr.type = 'outgoing_chat_message'
),
valid_responses as (
    select 
        entity_id,
        client_message_id,
        manager_message_id,
        response_time_minutes,
        manager_id,
        case
            when extract(hour from manager_time) <= 9 and extract(minute from manager_time) < 30 then 1
            else
                response_time_minutes
        end as valid_response_time
    from manager_responses
)
---
select m.name_mop as manager_name,
avg(vr.valid_response_time) as avg_response_time_minutes
from valid_responses vr
join test.managers m on m.mop_id = vr.manager_id
group by m.name_mop
order by avg_response_time_minutes;
