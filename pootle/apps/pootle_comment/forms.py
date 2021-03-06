# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
# Copyright (C) Zing contributors.
#
# This file is a part of the Zing project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.functional import cached_property

from django_comments.forms import CommentForm as DjCommentForm


User = get_user_model()


class CommentForm(DjCommentForm):
    user = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self, target_object, data=None, *args, **kwargs):
        if data:
            data["object_pk"] = str(target_object.pk)
            data["content_type"] = str(target_object._meta)
            if data.get("user"):
                data["user"] = str(data["user"].pk)

        super().__init__(target_object, data, *args, **kwargs)

        if data and data.get("user"):
            self.fields["name"].required = False
            self.fields["email"].required = False

    @cached_property
    def comment(self):
        return self.get_comment_object()

    def save(self):
        comment = self.comment
        comment.user = self.cleaned_data["user"]
        comment.submit_date = timezone.now()
        comment.save()


class UnsecuredCommentForm(CommentForm):
    def __init__(self, target_object, data=None, *args, **kwargs):
        super().__init__(target_object, data, *args, **kwargs)
        if data:
            data.update(self.generate_security_data())
