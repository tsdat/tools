import ruamel.yaml.comments


def Inline(*line):
    """Better display for inline lists

    ```yaml
    # Using Inline style
    dtype: [time]

    # The default style
    dtype:
        - time
    ```
    """
    ret = ruamel.yaml.comments.CommentedSeq(line)
    ret.fa.set_flow_style()
    return ret
