cognixcore.serializers
======================

.. py:module:: cognixcore.serializers

.. autoapi-nested-parse::

   A collection of what might prove to be usefull serializers



Classes
-------

.. autoapisummary::

   cognixcore.serializers.ComplexSerializer
   cognixcore.serializers.FractionSerializer


Module Contents
---------------

.. py:class:: ComplexSerializer

   Bases: :py:obj:`cognixcore.base.BasicSerializer`


   This default implementation simply returns the object as is. Useful
   for types that are already JSON compatible.


   .. py:method:: serialize(obj: complex) -> dict

      Serializes the object



   .. py:method:: deserialize(data) -> complex

      Deserializes the object from the data



.. py:class:: FractionSerializer

   Bases: :py:obj:`cognixcore.base.BasicSerializer`


   This default implementation simply returns the object as is. Useful
   for types that are already JSON compatible.


   .. py:method:: serialize(obj: fractions.Fraction)

      Serializes the object



   .. py:method:: deserialize(data) -> fractions.Fraction

      Deserializes the object from the data



