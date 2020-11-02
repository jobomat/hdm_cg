# coding: utf-8
import pymel.core as pc
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as omanim


def createAnimCurvesFromOptical(take, fps, tangentType=omanim.MFnAnimCurve.kTangentLinear):
    timestretch = take.rate / fps
    timelist = [om.MTime(float(x / timestretch)) for x in range(take.length)]
    animCurveNodes = {}
    for segmentName, trajectories in take.segments.items():
        animCurveNodes[segmentName] = []
        for i, trajectory in enumerate(trajectories):
            animcurve = omanim.MFnAnimCurve()
            animcurve.create(omanim.MFnAnimCurve.kAnimCurveTL)
            name = animcurve.setName(
                "{}_{}_{}_c{}".format(take.actor, take.takename, segmentName, i)
            )
            if len(timelist) > len(trajectory):
                trajectory.extend([0.0 for x in range(len(timelist) - len(trajectory))])
            animcurve.addKeys(timelist, trajectory, tangentType, tangentType)
            animCurveNodes[segmentName].append(pc.PyNode(name))
    return animCurveNodes
