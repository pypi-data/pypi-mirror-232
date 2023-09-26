=======================================
Document Recommendations
=======================================

.. _document-recommendations:

How to organize multiple documents?
=======================================
There are different types of technical documents for different perspectives or use cases. 
For instance, a manager or new-comer might first want to learn more about the features of a product on a high level, 
whereas a developer needs hints and recommendations how to integrate the software into a product.
Hence, for the organization of multiple documents we recommend a structure similar to:

**Product Description** for managers, decision-makers and new-comers

   This part of the documentation should contain a **description of the actual product**.
   These documents should answer the question: ``What's inside the black box?``
   This could be an overview of the architecture, the product features,
   the version history, performance values, licence information, etc.

**Integration Guides** for developers and integrators

   This part of the documentation should contain guides that are useful for an integrator using 
   our software inside a product.
   Those guides are supposed to answer the question: ``How to interface with the black box?`` 
   Example documents with audio-coding context would cover transport related details, 
   synchronization with video or other inputs that affect the time-variant behavior of the Fraunhofer software.

**Testing** for testers

   This section should contain details about Fraunhofer's internal testing, 
   testing methods we can offer for testing integrations, compliance and certification information 
   (e.g. MPEG conformance or available device level tests)
   Trademark information might also be added here.

**API Description** for reference

   The API description should contain detailed information about the API.
   In case of C/C++, Doxygen and breathe can take care of this.

How to organize a single document?
=======================================

Please stick to this order of headings:

.. code-block:: rst

   ==============
   Document title
   ==============

.. code-block:: rst

   Chapters
   ========

.. code-block:: rst

   Section
   -------

.. code-block:: rst
   
   Subsection
   ~~~~~~~~~~
