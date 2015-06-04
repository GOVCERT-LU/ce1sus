from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import BigInteger

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.indicator import Killchain
from ce1sus.db.common.session import Base


_REL_TTPS_KILLCHAINS = Table('rel_ttps_killchains', Base.metadata,
                             Column('rtk_id', BigInteger, primary_key=True, nullable=False, index=True),
                             Column('ttps_id', BigInteger, ForeignKey('ttpss.ttps_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                             Column('killchain_id', BigInteger, ForeignKey('killchains.killchain_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                             )


class TTPs(ExtendedLogingInformations, Base):
  event = relationship('Event', uselist=False)
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  kill_chains = relationship('Killchain', secondary='rel_ttps_killchains')
