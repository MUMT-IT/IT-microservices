#! -*- coding: utf-8 -*-
from datetime import datetime
from main import db, ma
from marshmallow import fields

author_abstracts = db.Table('author_abstracts',
        db.Column('author_id', db.Integer,
            db.ForeignKey('scopus_authors.id')),
        db.Column('abstract_id', db.Integer,
            db.ForeignKey('scopus_abstracts.id')))

funding_abstracts = db.Table('funding_abstracts',
        db.Column('abstract_id', db.Integer,
            db.ForeignKey('scopus_abstracts.id')),
        db.Column('funding_id', db.Integer,
            db.ForeignKey('fundings.id')))

# area_abstracts = db.Table('area_abstracts',
#         db.Column('area_id', db.Integer,
#             db.ForeignKey('scopus_areas.id')),
#         db.Column('abstract_id', db.Integer,
#             db.ForeignKey('scopus_abstracts.id')))

class ScopusAffiliation(db.Model):
    __tablename__ = 'scopus_affiliations'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.UnicodeText(), index=True)
    city = db.Column(db.UnicodeText())
    country = db.Column(db.UnicodeText())
    scopus_affil_id = db.Column(db.UnicodeText())

    def __repr__(self):
        return "<ScopusAffiliation id=%s>" % self.affil_id


class ScopusAuthor(db.Model):
    __tablename__ = 'scopus_authors'
    id = db.Column(db.Integer(), primary_key=True)
    affil_id = db.Column(db.Integer(),
                db.ForeignKey('scopus_affiliations.id'))
    initials = db.Column(db.String(8))
    #indexed_name = db.Column(db.String(255))
    surname = db.Column(db.UnicodeText())
    given_name = db.Column(db.UnicodeText())
    preferred_name = db.Column(db.UnicodeText())
    url = db.Column(db.Text())
    affiliation = db.relationship('ScopusAffiliation',
                    backref=db.backref('authors', lazy='dynamic'))

    def __repr__(self):
        return "<ScopusAuthor name=%s>" % \
                (self.indexed_name.encode('utf8'))


class ScopusAbstract(db.Model):
    __tablename__ = 'scopus_abstracts'
    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.Text())
    identifier = db.Column(db.UnicodeText())
    pii = db.Column(db.UnicodeText())
    doi = db.Column(db.UnicodeText())
    eid = db.Column(db.UnicodeText())
    title = db.Column(db.Text())
    publication_name = db.Column(db.UnicodeText())
    citedby_count = db.Column(db.Integer())
    cover_date = db.Column(db.DateTime())
    description = db.Column(db.UnicodeText())
    authors = db.relationship('ScopusAuthor',
                secondary=author_abstracts,
                backref=db.backref('abstracts', lazy='dynamic'))
    fundings = db.relationship('Funding',
                secondary=funding_abstracts,
                backref=db.backref('abstracts', lazy='dynamic'))

    def __repr__(self):
        return "<ScopusAbstract title=%s, doi=%s>" % \
                                (self.title[:20], self.doi)

class ScopusSubjArea(db.Model):
    __tablename__ = 'scopus_subj_areas'
    id = db.Column(db.Integer(), primary_key=True)
    affil_abbr = db.Column(db.String(32))
    year = db.Column(db.String(8))
    area = db.Column(db.String(8))
    articles = db.Column(db.Integer)
    citations = db.Column(db.Integer)


# class ScopusArea(db.Model):
#     __tablename__ = 'scopus_areas'
#     id = db.Column(db.Integer(), primary_key=True)
#     abstract_id = db.Column(db.Integer(),
#                     db.ForeignKey('scopus_abstracts.id'))
#     area = db.Column(db.String(255))
#     abstracts = db.relationship('ScopusAbstract',
#                         secondary=area_abstracts,
#                         backref=db.backref('areas', lazy='dynamic'))
#
#     def __repr__(self):
#         return "<ScopusArea area=%s>" % (self.area)


class Funding(db.Model):
    __tablename__ = 'fundings'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.UnicodeText())
    year = db.Column(db.UnicodeText())
    amount = db.Column(db.Float())

class AuthorSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    given_name = fields.String(required=True)
    surname = fields.String(required=True)
    abstracts = fields.Nested('AbstractSchema', many=True)
    url = ma.URLFor('api.researcherresource', id='<id>', _external=True)


class AbstractSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String(required=False)
    doi = fields.String()
    citedby_count = fields.Integer()
    cover_date = fields.DateTime()
    url = ma.URLFor('api.abstractresource', id='<id>', _external=True)


class ScopusAbstractCount(db.Model):
    __tablename__ = 'abstract_count'
    id = db.Column(db.Integer(), primary_key=True)
    institute = db.Column(db.String(128))
    year = db.Column(db.Integer())
    articles = db.Column(db.Integer())
    citations = db.Column(db.Integer())
