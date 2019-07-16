# encoding: utf-8

import gvsig
import sys

from gvsig import uselib
uselib.use_plugin("org.gvsig.topology.app.mainplugin")

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator
from org.gvsig.topology.lib.api import TopologyLocator
from org.gvsig.topology.lib.spi import AbstractTopologyRule

from deletePointAction import DeletePointAction

class MustBeProperlyInsidePolygonsPointRule(AbstractTopologyRule):
    
    geomName = None
    expression = None
    expressionBuilder = None
    
    def __init__(self, plan, factory, tolerance, dataSet1, dataSet2):
        AbstractTopologyRule.__init__(self, plan, factory, tolerance, dataSet1, dataSet2)
        self.addAction(DeletePointAction())
    
    def check(self, taskStatus, report, feature1):
        try:
            store2 = self.getDataSet2().getFeatureStore()
            if self.expression == None:
                manager = ExpressionEvaluatorLocator.getManager()
                self.expression = manager.createExpression()
                self.expressionBuilder = manager.createExpressionBuilder()
                self.geomName = store2.getDefaultFeatureType().getDefaultGeometryAttributeName()
            point1 = feature1.getDefaultGeometry()
            tolerance1 = self.getTolerance()
            theDataSet2 = self.getDataSet2()
            if theDataSet2.getSpatialIndex() != None:
                if point1.getGeometryType().getName() == "Point2D":
                    buffer1 = point1.buffer(tolerance1)
                    contains = False
                    for featureReference in theDataSet2.query(buffer1):
                        feature2 = featureReference.getFeature()
                        polygon2 = feature2.getDefaultGeometry()
                        if polygon2.getGeometryType().getName() == "Polygon2D":
                            if buffer1.intersects( polygon2 ):
                                contains = True
                                break
                        else:
                            if polygon2.getGeometryType().getName() == "MultiPolygon2D":
                                n2 = polygon2.getPrimitivesNumber()
                                for i in range(0, n2 + 1):
                                    surface2 = polygon2.getSurfaceAt(i)
                                    if buffer1.intersects( surface2 ):
                                        contains = True
                                        break
                    if not contains:
                        report.addLine(self,
                                    self.getDataSet1(),
                                    self.getDataSet2(),
                                    point1,
                                    point1,
                                    feature1.getReference(), 
                                    None,
                                    False,
                                    "The point is not contained by polygon."
                        )
                else:
                    if point1.getGeometryType().getName() == "MultiPoint2D":
                        n1 = point1.getPrimitivesNumber()
                        for i in range(0, n1 + 1):
                            buffer1 = point1.getPointAt(i).buffer(tolerance1)
                            contains = False
                            for featureReference in theDataSet2.query(buffer1):
                                feature2 = featureReference.getFeature()
                                polygon2 = feature2.getDefaultGeometry()
                                if polygon2.getGeometryType().getName() == "Polygon2D":
                                    if buffer1.intersects( polygon2 ):
                                        contains = True
                                        break
                                else:
                                    if polygon2.getGeometryType().getName() == "MultiPolygon2D":
                                        n2 = polygon2.getPrimitivesNumber()
                                        for j in range(0, n2 + 1):
                                            surface2 = polygon2.getSurfaceAt(j)
                                            if buffer1.intersects( surface2 ):
                                                contains = True
                                                break
                            if not contains:
                                report.addLine(self,
                                            self.getDataSet1(),
                                            self.getDataSet2(),
                                            point1.getPointAt(i),
                                            point1.getPointAt(i),
                                            feature1.getReference(), 
                                            None,
                                            False,
                                            "The multipoint is not contained by polygon."
                                )
        except:
            ex = sys.exc_info()[1]
            gvsig.logger("Can't execute rule. Class Name: " + ex.__class__.__name__ + ". Exception: " + str(ex), gvsig.LOGGER_ERROR)

def main(*args):
    pass