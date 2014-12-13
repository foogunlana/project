
from mongoengine import StringField, Document, connect

connect('stears')

class Member(Document):
	name = StringField(max_length=20)
	email = StringField(max_length=20)

	def __unicode__(self):
		return unicode(self.name)
