parameters = {
    "camera": ["s3_cam", "s3a_cam"],
    "frames":["1-20", "22", "30-35"],
    "outdir": ["L:/test/renders"],
    "padding": [3],
    "percentres": [50.0],
    "projdir": ["L:/test"],
    "scene": ["L:/test/scenes/shots/shot03-06/s03.ma", "L:/test/scenes/shots/shot03-06/s03a.ma"]
}

renderer = "Arnold Renderer/2020_ca"


def create_renderpal_renderset(renderer, parameters):
    rset = [
        "<RenderSet>",
        "\t<Renderer>{}</Renderer>".format(renderer),
        "\t\t<Values>"
    ]

    for parameter, values in parameters.items():
        rset.append("\t\t<{}>".format(parameter))
        for value in values:
            rset.append("\t\t\t<Value>{}</Value>".format(
                str(value).replace("/", "\\\\")
            ))
        rset.append("\t\t</{}>".format(parameter))

    rset.extend(["\t</Values>","</RenderSet>"])
    return "\n".join(rset)

print(create_renderpal_renderset(renderer, parameters))