============================================
Create your own Ansys Sound Docker container
============================================

The Ansys Sound service is based on the Ansys **DPF Server**, and its **DPF Sound plugin**. It is
notably used by `PyAnsys Sound <https://sound.docs.pyansys.com/version/dev/index.html>`_
(``ansys-sound-core`` package).

You can create your own service using a Docker container image that includes both the **DPF Server**
and the **DPF Sound plugin**. The provided example file `Dockerfile.windows
<https://github.com/ansys/pyansys-sound/blob/main/docker/Dockerfile.windows>`_ shows how to create
such a Docker image.

Note that the provided version of the Dockerfile works with:

- **Windows 11** host. If you want to use a different Windows host, modify the ``BASE_IMAGE``
  argument at the top of the file.
- Version **2025.2.pre0** of **DPF Server** and **DPF Sound**. If you want to use a different
  version of DPF Server and DPF Sound, modify the ``DPF_PACKAGE_VERSION`` and
  ``DPF_PACKAGE_VERSION_NO_DOTS`` arguments at the top of the file.

Build the Ansys Sound Docker image
----------------------------------

For building the image, follow these steps:

#. Make sure Docker is installed on your machine.
#. Get the **DPF Server** and the **DPF Sound plugin** from the `Ansys Developer Portal
   <https://download.ansys.com/Others/DPF%20Pre-Release>`_.
#. Extract the 2 downloaded zip files to a local folder, and merge together the ``ansys`` folders
   within.
#. Move the provided ``Dockerfile.windows`` file next to the merged folder ``ansys``.
#. Open a command prompt, and navigate to the folder containing the ``Dockerfile.windows`` file and
   the ``ansys`` folder.
#. Build the Docker image with the following command:

   ``docker build --file Dockerfile.windows . --tag <your_image_name> -m 2GB --no-cache``

   Replace ``<your_image_name>`` with a name of your choice, for example, run:

   ``docker build --file Dockerfile.windows . --tag dpf_sound_image -m 2GB --no-cache``

#. After the build is done, run the container with the following command:

   ``docker run -d -e "ANSYS_DPF_ACCEPT_LA=Y" -e "ANSYSLMD_LICENSE_FILE=<your_license_info>" -p <host_port>:50052 --name <your_container_name> <your_image_name>``

   Replace ``<your_license_info>`` with your actual license information (license file or license
   server info, see `Licensing
   <https://dpf.docs.pyansys.com/version/stable/getting_started/licensing.html>`_ for details),
   ``<host_port>`` with a suitable localhost port number, ``<your_container_name>`` with a name of
   your choice, and ``<your_image_name>`` with the name set previously. Note the ``--name
   <your_container_name>`` part is optional.
   For example, run:

   ``docker run -d -p 6780:50052 --name dpf_sound_container dpf_sound_image``

#. The container is now running, and you can connect to it, for example, in Python with (using the
   port number set previously):

   ``from ansys.dpf.core.server import connect_to_server
   server = connect_to_server(port=<host_port>)``

   or, with **PyAnsys Sound**:

   ``from ansys.sound.core.server_helpers import connect_to_or_start_server
   server = connect_to_or_start_server(port=<host_port>)``


VPN note
--------

If you are using a VPN (virtual private network), there is a high chance that the Docker container
cannot be used, because of the address redirections done by the VPN. You will be able to build the
Docker image and run the container, but you won't be able to connect to it.

