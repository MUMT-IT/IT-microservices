from main import db, ma, me

class SurveyCategory(db.Model):
    __tablename__ = 'survey_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

class SurveyQuestion(db.Model):
    __tablename__ = 'survey_questions'
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer, db.ForeignKey('survey_categories.id'))
    category = db.relationship('SurveyCategory',
                    backref=db.backref('questions', lazy='dynamic'))
    question = db.Column(db.String(128), nullable=False)
    year = db.Column(db.String(4), nullable=False)

class SurveyAnswer(db.Model):
    __tablename__ = 'survey_answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.String(128), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    qid = db.Column(db.Integer, db.ForeignKey('survey_questions.id'))
    question = db.relationship('SurveyQuestion',
                    backref=db.backref('answers', lazy='dynamic'))

class SurveyWRSSummary(db.Model):
    __tablename__ = 'survey_wrs_summary'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(4), nullable=False)
    post = db.Column(db.Boolean())
    question = db.Column(db.String(128), nullable=False)
    value = db.Column(db.String(16), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('survey_categories.id'))

class SurveyWRSTeachingSummary(db.Model):
    __tablename__ = 'survey_wrs_teaching_summary'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(4), nullable=False)
    method = db.Column(db.String(64))
    question = db.Column(db.String(128), nullable=False)
    value = db.Column(db.String(16), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('survey_categories.id'))


class AcademicProgram(db.Model):
    __tablename__ = 'academic_programs'
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String())
    degree_title = db.Column(db.String(128))
    degree_title_abbr = db.Column(db.String(32))
    program_title = db.Column(db.String(128))
    program_title_abbr = db.Column(db.String(32))

class FollowUpSummary(db.Model):
    __tablename__ = 'follow_up_summary'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer,
                        db.ForeignKey('academic_programs.id'))
    post_grad_employment_rate = db.Column(db.Float())
    survey_year = db.Column(db.Integer())


class EvaluationSummary(db.Model):
    __tablename__ = 'evaluation_summary'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer,
                        db.ForeignKey('academic_programs.id'))
    survey_year = db.Column(db.Integer())
    avg_analytics = db.Column(db.Float())
    avg_professional = db.Column(db.Float())
    avg_thinking = db.Column(db.Float())
    avg_relation = db.Column(db.Float())
    avg_knowledge = db.Column(db.Float())
    avg_morals = db.Column(db.Float())
    avg_identity = db.Column(db.Float())
    avg_overall = db.Column(db.Float())


class WRSEdpexScore(me.EmbeddedDocument):
    year = me.IntField()
    score = me.FloatField()


class WRSEdpexTopic(me.Document):
    desc = me.StringField()
    slug = me.StringField()
    scores = me.EmbeddedDocumentListField(WRSEdpexScore, default=[])
