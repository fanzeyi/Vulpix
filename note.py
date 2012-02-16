# -*- coding: utf-8 -*-

from tornado.web import HTTPError
from tornado.web import authenticated

from judge import Note
from judge import NoteDBMixin
from judge import MemberDBMixin
from judge import ProblemDBMixin
from judge.base import BaseHandler
from judge.utils import escape

class NoteHandler(BaseHandler, NoteDBMixin, MemberDBMixin, ProblemDBMixin):
    def get(self, nid):
        try:
            nid = int(nid)
        except ValueError:
            raise HTTPError(404)
        note = self.select_note_by_id(nid)
        if note:
            title = note.title
            member = self.select_member_by_id(note.member_id)
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((member.username, '/member/%s' % member.username))
            breadcrumb.append((self._('Note'), '/member/%s/notes' % member.username))
            breadcrumb.append((note.title, '/note/%d' % note.id))
            related_problem = []
            if note.link_problem:
                for pid in note.link_problem:
                    related_problem.append(self.select_problem_by_id(pid))
            self.render("note.html", locals())
        else:
            raise HTTPError(404)

class CreateNoteHandler(BaseHandler, NoteDBMixin):
    @authenticated
    def get(self):
        nid = self.get_argument("nid", default = None)
        note = None
        note_page = True
        breadcrumb = []
        breadcrumb.append((self._('Home'), '/'))
        breadcrumb.append((self.current_user.username, '/member/%s' % self.current_user.username))
        breadcrumb.append((self._('Note'), '/member/%s/notes' % self.current_user.username))
        if nid:
            note = self.select_note_by_id(nid)
            if note.member_id != self.current_user['id']:
                raise HTTPError(403)
            breadcrumb.append((self._('Edit Note'), '/note/create?nid=%s' % nid))
        else:
            breadcrumb.append((self._('Write Note'), '/note/create'))
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
        error.extend(self._check_text_value(notetitle, "Note Title", True, 100))
        error.extend(self._check_text_value(content, "Content", True, 30000))
        note.title = self.xhtml_escape(notetitle)
        note.content = self.xhtml_escape(content)
        note.link_problem = [self.xhtml_escape(problem) for problem in link_problem]
        note.id = int(nid) if nid else None
        if error:
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((self.current_user.username, '/member/%s' % self.current_user.username))
            breadcrumb.append((self._('Note'), '/member/%s/notes' % self.current_user.username))
            note_page = True
            if note.id:
                title = self._("Edit Note")
                breadcrumb.append((self._('Edit Note'), '/note/create?nid=%s' % nid))
            else:
                title = self._("Write Note")
                breadcrumb.append((self._('Write Note'), '/note/create'))
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
            breadcrumb = []
            breadcrumb.append((self._('Home'), '/'))
            breadcrumb.append((member.username, '/member/%s' % member.username))
            breadcrumb.append((self._('Note'), '/member/%s/notes' % member.username))
            start = self.get_argument("start", default = 0)
            notes = self.select_note_by_mid(member.id, start = start)
            title = member.username + self._("'s Note")
            self.render("member_note.html", locals())
        else:
            raise HTTPError(404)
