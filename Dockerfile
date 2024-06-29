# Use a lightweight Ubuntu image as a base
FROM odoo:17


# Clone Odoo source code from GitHub
#RUN git clone --depth 1 --branch 17.0 https://github.com/odoo/odoo.git /opt/odoo

# Set the working directory
WORKDIR /opt/odoo

# Copy the local dz_accounting directory to the container
COPY ./etc /etc/odoo

COPY ./addons /mnt/extra-addons
#RUN chmod -R 777 /addons
#WORKDIR /mnt/extra-addons
#RUN chmod -R 777 /mnt/extra-addons
#RUN mv /p/extra-addons/* /mnt/extra-addons
# Move contents of dz_accounting to /mnt/extra-addons
#RUN mv /addons/* /mnt/extra-addons/

# Install Python dependencies
#RUN pip3 install -r requirements.txt

# Expose the Odoo port
#EXPOSE 8069

# Command to start Odoo
CMD ["odoo"]