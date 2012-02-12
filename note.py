# -*- coding: utf-8 -*-

from tornado.web import authenticated

from judge import Note
from judge import NoteDBMixin
from judge import MemberDBMixin
from judge.base import BaseHandler
from judge.utils import escape

class CreateNoteHandler(BaseHandler, NoteDBMixin):
    @authenticated
    def get(self):
        title = self._("Write Note")
        self.render("note_create.html", locals())
    @authenticated
    def post(self):
        notetitle = self.get_argument("notetitle", default = None)
        content = self.get_argument("content", default = None)
        error = []
        error.extend(self._check_text_value(notetitle, "Note Title", True))
        error.extend(self._check_text_value(content, "Content", True))
        notetitle = self.xhtml_escape(notetitle)
        content = self.xhtml_escape(content)
        if error:
            title = self._("Write Note")
            self.render("note_create.html", locals())
            return
        note = Note()
        note.title = notetitle
        note.content = content
        note.member_id = self.current_user['id']
        self.insert_note(note)
        self.redirect("/note/%d" % note.id)
