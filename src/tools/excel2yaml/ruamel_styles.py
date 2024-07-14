import ruamel.yaml.comments


def ListInline(items: list[str]):
    """Better display for inline lists

    ```yaml
    # Using ListInline style
    dtype: [time]

    # The default style
    dtype:
        - time
    ```
    """
    ret = ruamel.yaml.comments.CommentedSeq(items)
    ret.fa.set_flow_style()
    return ret
