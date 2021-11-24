from model import *


# common method
def create_entry(model_class, *, commit=True, **kwargs):
    session = Session()
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    return entry

# user methods


def get_user(model_class, nick, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(UserName=nick).one()


def delete_user(model_class, nick, **kwargs):
    session = Session()
    to_return = session.query(model_class).filter_by(UserName=nick).one()
    session.query(model_class).filter_by(UserName=nick).delete()
    session.commit()
    return to_return


def update_user(entry, *, commit=True, **kwargs):
    session = Session()
    for key, value in kwargs.items():
        setattr(entry, key, value)
    if commit:
        session.commit()
    return entry

def return_account_num_objects(model_class, user_name, **kwargs):
    session = Session()
    # user_to_del = session.query(User).filter_by(UserName=user_name).one()
    return session.query(model_class).filter_by(UserName=user_name).all()



def delete_user_accounts(model_class, nick, **kwargs):
    session = Session()
    #session.query(model_class).filter_by(UserName=nick).delete()
    all_acc = session.query(model_class).filter_by(UserName=nick).all()


# account methods


def get_account(model_class, number, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(AccountNumber=number).one()


def delete_account(model_class, number, **kwargs):
    session = Session()
    to_return = session.query(model_class).filter_by(AccountNumber=number).one()
    session.query(model_class).filter_by(AccountNumber=number).delete()
    session.commit()
    return to_return


def update_account(entry, *, commit=True, **kwargs):
    session = Session()
    for key, value in kwargs.items():
        setattr(entry, key, value)
    if commit:
        session.commit()
    return entry

# transfer methods

def get_transfer(model_class, t_id, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(idTransfer=t_id).one()



