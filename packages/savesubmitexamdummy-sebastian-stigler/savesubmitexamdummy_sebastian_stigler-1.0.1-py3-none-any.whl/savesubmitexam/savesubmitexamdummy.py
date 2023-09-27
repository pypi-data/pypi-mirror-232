class SaveSubmit:
    """Run the submission form
    =======================

        SaveSubmit().run_<lang>_<exam_type>_<course>()

    Where

    * <lang> is either ``de`` for german or ``en`` for english,
    * <exam_type> is either ``testexam`` or ``exam`` and
    * <course> is the name of the course from the `config.yaml` of
      ExamUploader.

    Please use in the <course> underscores wherever you used hyphens in
    the ``config.yaml`` file.

    Example:
    --------

    You want the german form for a testexam for the course 23w-python101,
    then you call:

        SaveSubmit().run_de_testexam_23w_python101()
    ----------------------------------------------------------------------
    """

    def __getattr__(self, name):
        return lambda: None
