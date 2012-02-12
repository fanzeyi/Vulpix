# -*- coding: utf-8 -*-

from tornado.web import HTTPError
from tornado.web import authenticated

from judge import Note
from judge import NoteDBMixin
from judge import MemberDBMixin
from judge.base import BaseHandler
from judge.utils import escape

class NoteHandler(BaseHandler, NoteDBMixin):
    def get(self, nid):
        try:
            nid = int(nid)
        except ValueError:
            raise HTTPError(404)
        note = self.select_note_by_id(nid)
        if note:
            title = note.title
            self.render("note.html", locals())
        else:
            raise HTTPError(404)

class CreateNoteHandler(BaseHandler, NoteDBMixin):
    @authenticated
    def get(self):
        nid = self.get_argument("nid", default = None)
        note = None
        if nid:
            note = self.select_note_by_id(nid)
            if note.member_id != self.current_user['id']:
                raise HTTPError(403)
        title = self._("Write Note")
        self.render("note_create.html", locals())
    @authenticated
    def post(self):
        notetitle = self.get_argument("notetitle", default = None)
        content = self.get_argument("content", default = None)
        nid = self.get_argument("nid", default = None)
        link_problem = self.get_arguments("link_problem[]")
        note = Note()
        error = []
        error.extend(self._check_text_value(notetitle, "Note Title", True))
        error.extend(self._check_text_value(content, "Content", True))
        note.title = self.xhtml_escape(notetitle)
        note.content = self.xhtml_escape(content)
        note.link_problem = [self.xhtml_escape(problem) for problem in link_problem]
        note.id = int(nid) if nid else None
        if error:
            title = self._("Write Note")
            self.render("note_create.html", locals())
            return
        note.member_id = self.current_user['id']
        if note.id:
            self.update_note(note)
        else:
            self.insert_note(note)
        self.redirect("/note/%d" % note.id)

class DeleteNoteHandler(BaseHandler, NoteDBMixin):
    @authenticated
    def get(self, nid):
        try:
            nid = int(nid)
        except ValueError:
            raise HTTPError(404)
        note = self.select_note_by_id(nid)
        if note.member_id != self.current_user["id"]:
            raise HTTPError(403)
        self.delete_note_by_nid(nid)
        self.redirect("/member/%s/notes" % self.current_user["username"])

class MemberNotesHandler(BaseHandler, MemberDBMixin, NoteDBMixin):
    def get(self, username):
        member = self.select_member_by_username(username)
        if member:
            start = self.get_argument("start", default = 0)
            notes = self.select_note_by_mid(member.id, start = start)
            title = member.username + self._("'s Note")
            self.render("member_note.html", locals())
        else:
            raise HTTPError(404)
