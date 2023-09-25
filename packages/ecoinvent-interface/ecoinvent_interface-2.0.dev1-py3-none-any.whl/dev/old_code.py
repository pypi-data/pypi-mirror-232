
    def get_db_sui(self, spdx: str):
        """
        From the given spdx string, get the version and system model
        :param spdx:
        :return:
        """
        system_models = set([vsm[1] for vsm in self.db_dict])
        if re.match(rf'ei-\d.\d-[{("|".join(system_models))}]', spdx) is None:
            raise KeyError(
                "The provided database name does not have the correct format."
                "Use ei-<version>-<system model>. "
                'System models are ["cutoff", "apos", "consequential", "EN15804"]'
            )

        db_sui_db, db_sui_version, db_sui_sm = spdx.split("-")
        available_spdx = [f"ei-{tup[0]}-{tup[1]}" for tup in self.db_dict.keys()]
        if not (db_sui_version, db_sui_sm) in self.db_dict.keys():
            raise KeyError(
                f"The provided database does not exist online."
                f"Choose one of the following: {available_spdx}"
            )
        return db_sui_version, db_sui_sm

    @logged_in
    def get_webpage(self, activity_name, geography, reference_product, open_tab=True):
        spdx = f"ei-{self.version}-{self.system_model}"
        file_path = os.path.join(CachedStorage.eidl_dir, f"{spdx}_url_ids.csv")
        if not os.path.exists(file_path):
            self._download_mapping(spdx=spdx, saveto=file_path)
        with open(file_path, mode="r") as f:
            csvfile = csv.reader(f)
            for line in csvfile:
                if line[0:3] == [activity_name, geography, reference_product]:
                    pdf_id = line[-1]
                    break

        url = "https://v{db_num}.ecoquery.ecoinvent.org/Details/UPR/{pdf_id}".format(
            db_num=self.version.replace(".", ""),
            pdf_id=pdf_id,
        )
        if open_tab:
            webbrowser.open_new_tab(url)
        else:
            return url

    @logged_in
    def get_pdf(self, activity_name, geography, reference_product):
        """
        Given the input parameters, download a PDF from ecoinvent's website.
        :param activity_name
        :param geography
        :param reference_product
        """
        spdx = f"ei-{self.version}-{self.system_model}"
        file_path = os.path.join(CachedStorage.eidl_dir, f"{spdx}_url_ids.csv")
        if not os.path.exists(file_path):
            self._download_mapping(spdx=spdx, saveto=file_path)
        with open(file_path, mode="r") as f:
            csvfile = csv.reader(f)
            for line in csvfile:
                if line[0:3] == [activity_name, geography, reference_product]:
                    pdf_id = line[-1]
                    break
        pdf_url = self._get_pdf_url(self.version, pdf_id)
        pdf_filename = f"ei-{self.version}-{self.system_model} {activity_name}-{geography}-{reference_product}.pdf"
        self._download_one(pdf_url, pdf_filename)


def get_pdf(spdx, activity_name, geography, reference_product, **kwargs):
    """
    Download a PDF file identified with the given params
    :param spdx: the spdx string to identify ecoinvent's version and system model
    :param activity_name: the activity name
    :param geography: the geography
    :param reference_product: the reference product
    """
    downloader = EcoinventInterface(**kwargs)
    downloader.login()
    downloader.db_dict = downloader.get_available_files()
    downloader.set_with_spdx(spdx)
    downloader.get_pdf(activity_name, geography, reference_product)
