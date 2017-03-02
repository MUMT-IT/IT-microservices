from main import db, ma

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