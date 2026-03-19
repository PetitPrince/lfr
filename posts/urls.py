from django.urls import path

from posts.views import (
    CommentCreateView,
    CommentReplyView,
    DiscoverFacultyView,
    DiscoverOtherView,
    DiscoverStudentsView,
    MessageBoardView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostEditView,
    PostExpandView,
    StudentFilterView,
    StudentRandomView,
)

app_name = "posts"

urlpatterns = [
    path("<slug:slug>/", MessageBoardView.as_view(), name="message_board"),
    path("<slug:slug>/create/", PostCreateView.as_view(), name="post_create"),
    path("<slug:slug>/post/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("<slug:slug>/post/<int:pk>/edit/", PostEditView.as_view(), name="post_edit"),
    path("<slug:slug>/post/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("<slug:slug>/post/<int:pk>/expand/", PostExpandView.as_view(), name="post_expand"),
    path("<slug:slug>/post/<int:pk>/comment/", CommentCreateView.as_view(), name="comment_create"),
    path("<slug:slug>/post/<int:pk>/comment/<int:comment_id>/reply/", CommentReplyView.as_view(), name="comment_reply"),
    path("<slug:slug>/discover/faculty/", DiscoverFacultyView.as_view(), name="discover_faculty"),
    path("<slug:slug>/discover/students/", DiscoverStudentsView.as_view(), name="discover_students"),
    path("<slug:slug>/discover/students/filter/", StudentFilterView.as_view(), name="student_filter"),
    path("<slug:slug>/discover/students/random/", StudentRandomView.as_view(), name="student_random"),
    path("<slug:slug>/discover/other/", DiscoverOtherView.as_view(), name="discover_other"),
]
