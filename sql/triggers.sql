# тригер для каскадного видалення юзера

DELIMITER $$
CREATE TRIGGER casc_del_user2
before delete on user
for each row
begin

    delete from transfer where fromAccountNumber = any
		(select distinct(a.AccountNumber)
		from account a inner join user u on a.UserName = old.UserName
        order by a.AccountNumber asc);

	delete from transfer where toAccountNumber = any
		(select distinct(a.AccountNumber)
		from account a inner join user u on a.UserName = old.UserName
        order by a.AccountNumber asc);

	delete from account where UserName = old.UserName;

end $$
delimiter ;


DELIMITER $$
CREATE TRIGGER casc_del_account
before delete on account
for each row
begin

    delete from transfer where fromAccountNumber =  old.AccountNumber;
	delete from transfer where toAccountNumber =  old.AccountNumber;

end $$
delimiter ;