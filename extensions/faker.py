from faker import Faker
from jinja2.ext import Extension

def name() -> str:
	en_US_faker = Faker('en_US')
	return en_US_faker.name()

def paragraph(nb_list: list) -> str:
	en_US_faker = Faker('en_US')
	res_str = ""
	nb_sentences = nb_list[0] if len(nb_list) > 0 else 5
	nb_words = nb_list[1] if len(nb_list) > 1 else 15
	prefix = nb_list[2] if len(nb_list) > 2 else ""
	for _ in range(nb_sentences):
		res_str += (prefix + en_US_faker.sentence(nb_words=nb_words) + "\n")
	return res_str

class FakerExtension(Extension):
	def __init__(self, environment):
		super().__init__(environment)
		environment.filters["paragraph"] = paragraph
		environment.filters["name"] = name